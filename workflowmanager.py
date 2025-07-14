import os
import pandas as pd
from langgraph.graph import StateGraph, END, MessagesState
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

from src.tools import query_snowflake
from src.llm_manager import LLMManager
import src.schema_prompt as sp
import src.summary_prompt as sum_prompt


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

        # Add nodes
        workflow.add_node("snowflake_query_agent", self.call_snowflake_model)
        workflow.add_node("tools", self.call_tools_node)  # 🔧 FIXED: custom tool node
        workflow.add_node("summary_agent", self.call_summary_model)

        # Entry point
        workflow.set_entry_point("snowflake_query_agent")

        # Retry-aware conditional transitions
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
            user_msg = next(m for m in reversed(state["messages"]) if isinstance(m, HumanMessage))
            system_prompt = sp.get_schema_prompt()
            response = self.llm_manager.invoke_model([
                SystemMessage(content=system_prompt),
                user_msg
            ])
            return {"messages": [response if isinstance(response, AIMessage) else AIMessage(content=str(response))]}
        except Exception as e:
            print(f"❌ Error in call_snowflake_model: {e}")
            return {"messages": [AIMessage(content=f"Error during snowflake query: {e}")]}

    def call_tools_node(self, state: MessagesState):
        print("🔧 Running tool manually...")
        try:
            query_msg = state["messages"][-1]
            tool = self.tools[0]  # Only one tool assumed
            tool_result = tool.invoke(query_msg)

            os.makedirs(os.path.dirname(self.csv_file_path), exist_ok=True)
            if isinstance(tool_result, pd.DataFrame):
                tool_result.to_csv(self.csv_file_path, index=False)
            elif isinstance(tool_result, str):
                with open(self.csv_file_path, "w") as f:
                    f.write(tool_result)

            print(f"✅ Tool output saved to: {self.csv_file_path}")
            return {
                "messages": [AIMessage(content="Tool execution successful.", tool_result=tool_result)]
            }

        except Exception as e:
            print(f"❌ Tool execution failed: {e}")
            return {
                "messages": [AIMessage(content=f"Tool execution failed: {e}")]
            }

    def call_summary_model(self, state: MessagesState):
        print("🧠 Entering summary generation...")
        try:
            summary_prompt = sum_prompt.get_summary_prompt_from_csv(os.path.basename(self.csv_file_path))

            if summary_prompt == "No summary can be generated.":
                return {"messages": [AIMessage(content=summary_prompt)]}

            response = self.llm_manager.invoke_model([
                SystemMessage(content=summary_prompt)
            ])

            return {"messages": [response if isinstance(response, AIMessage) else AIMessage(content=str(response))]}
        except Exception as e:
            print(f"❌ Error in call_summary_model: {e}")
            return {"messages": [AIMessage(content=f"Summary generation error: {e}")]}

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
