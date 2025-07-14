import os
import pandas as pd
from typing import Literal
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.tools import query_snowflake
from src.llm_manager import LLMManager
import src.schema_prompt as sp
import src.summary_prompt as sum_prompt


def get_latest_human_message(messages):
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg
    raise ValueError("❌ No HumanMessage found in state['messages']")


class WorkflowManager:
    """LangGraph agent that runs: query → tool → summarization, with retries."""

    def __init__(self):
        self.tools = [query_snowflake]
        self.llm_manager = LLMManager(self.tools)
        self.max_attempts = 3
        self.csv_file_path = "output/query_results.csv"
        self.state_graph = self.create_workflow()

    def create_workflow(self):
        workflow = StateGraph(MessagesState)

        workflow.add_node("snowflake_query_agent", self.call_snowflake_model)
        workflow.add_node("tools", self.call_tools_node)
        workflow.add_node("summary_agent", self.call_summary_model)

        workflow.set_entry_point("snowflake_query_agent")

        workflow.add_conditional_edges("snowflake_query_agent", self.retry_or_next("snowflake_query_agent", "tools"))
        workflow.add_conditional_edges("tools", self.retry_or_next("tools", "summary_agent"))
        workflow.add_conditional_edges("summary_agent", self.retry_or_next("summary_agent", END))

        return workflow.compile(checkpointer=MemorySaver())

    def retry_or_next(self, current_node, next_node):
        def condition(state: MessagesState):
            attempt_key = f"{current_node}_attempts"
            attempt_count = state.get(attempt_key, 0)

            if self.is_success(state):
                print(f"✅ {current_node} succeeded → moving to {next_node}")
                return next_node

            if attempt_count >= self.max_attempts:
                print(f"❌ {current_node} failed after {self.max_attempts} attempts → END")
                state["messages"].append(AIMessage(content=f"Step `{current_node}` failed after {self.max_attempts} attempts."))
                return END

            state[attempt_key] = attempt_count + 1
            print(f"🔁 Retrying {current_node}")
            return current_node
        return condition

    def is_success(self, state: MessagesState):
        for msg in reversed(state["messages"]):
            if hasattr(msg, "tool_result"):
                result = msg.tool_result
                if isinstance(result, str) and "error" not in result.lower():
                    return True
            elif isinstance(msg, AIMessage) and msg.content:
                return True
        return False

    def call_snowflake_model(self, state: MessagesState):
        try:
            user_msg = get_latest_human_message(state["messages"])
            system_prompt = sp.get_schema_prompt()
            response = self.llm_manager.invoke_model([
                SystemMessage(content=system_prompt),
                user_msg
            ])
            print("📡 Snowflake LLM query complete")
            return {"messages": [response if isinstance(response, AIMessage) else AIMessage(content=str(response))]}
        except Exception as e:
            print(f"❌ Error in call_snowflake_model: {e}")
            return {"messages": [AIMessage(content=f"Error during schema prompt step: {str(e)}")]}

    def call_tools_node(self, state: MessagesState):
        print("🔧 Executing tools node...")
        response = ToolNode(self.tools)(state)

        for msg in response["messages"]:
            if hasattr(msg, "tool_result"):
                result = msg.tool_result
                try:
                    os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
                    if isinstance(result, pd.DataFrame):
                        result.to_csv(self.csv_file_path, index=False)
                    elif isinstance(result, str):
                        with open(self.csv_file_path, "w") as f:
                            f.write(result)
                    print(f"📁 Tool result saved to: {self.csv_file_path}")
                except Exception as e:
                    print(f"❌ Failed to save CSV: {e}")
        return response

    def call_summary_model(self, state: MessagesState):
        print("🧠 Executing summary node...")
        try:
            summary_prompt = sum_prompt.get_summary_prompt_from_csv(os.path.basename(self.csv_file_path))
            if summary_prompt == "No summary can be generated.":
                return {"messages": [AIMessage(content=summary_prompt)]}

            response = self.llm_manager.invoke_model([
                SystemMessage(content=summary_prompt)
            ])
            print("✅ Summary generated")
            return {"messages": [response if isinstance(response, AIMessage) else AIMessage(content=str(response))]}
        except Exception as e:
            print(f"❌ Error in call_summary_model: {e}")
            return {"messages": [AIMessage(content=f"Error during summary generation: {str(e)}")]}

    def run(self, input_message, thread_id="summary-run-1"):
        initial_state = {
            "messages": [HumanMessage(content=input_message)]
        }
        final_state = self.state_graph.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})

        print("\n📨 Final Messages:")
        for msg in final_state["messages"]:
            print("-", type(msg), getattr(msg, "content", msg))

        for msg in reversed(final_state["messages"]):
            if isinstance(msg, AIMessage):
                return msg.content

        return "⚠️ No summary was generated."
