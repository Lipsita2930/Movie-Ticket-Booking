from langgraph.graph import StateGraph, END, MessagesState
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain.tools import tool

from src.tools import query_snowflake  # Ensure this is properly structured
from src.llm_manager import LLMManager
import src.schema_prompt as sp
import src.summary_prompt as sum_prompt


class WorkflowManager:
    """LangGraph agent that runs: query → tool → summarization, with retries."""

    def __init__(self):
        self.tools = [query_snowflake]
        self.llm_manager = LLMManager(self.tools)
        self.max_attempts = 3
        self.state_graph = self.create_workflow()

    def create_workflow(self):
        workflow = StateGraph(MessagesState)

        # Add nodes
        workflow.add_node("snowflake_query_agent", self.call_snowflake_model)
        workflow.add_node("tools", ToolNode(self.tools))
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

            print(f"[{current_node}] Attempt #{attempt_count + 1}")
            for i, m in enumerate(state["messages"]):
                print(f" Message {i}: {type(m).__name__} - {getattr(m, 'content', '')}")

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
        """Check if a successful tool_result or AI response exists."""
        for msg in reversed(state["messages"]):
            if hasattr(msg, "tool_result"):
                result = msg.tool_result
                if isinstance(result, str) and "error" not in result.lower():
                    return True
            elif isinstance(msg, AIMessage) and msg.content:
                return True
        return False

    def call_snowflake_model(self, state: MessagesState):
        user_msg = state['messages'][-1]
        system_prompt = sp.get_schema_prompt()
        response = self.llm_manager.invoke_model([
            SystemMessage(content=system_prompt),
            user_msg
        ])
        return {"messages": [response]}

    def call_summary_model(self, state: MessagesState):
        print("🧠 Entering summary generation...")
        try:
            summary_prompt = sum_prompt.get_summary_prompt_from_csv()

            if not summary_prompt or summary_prompt.strip() == "":
                return {"messages": [AIMessage(content="No summary can be generated.")]}

            response = self.llm_manager.invoke_model([
                SystemMessage(content=summary_prompt)
            ])

            return {"messages": [response if isinstance(response, AIMessage) else AIMessage(content=str(response))]}
        except Exception as e:
            print(f"❌ Error in call_summary_model: {e}")
            return {"messages": [AIMessage(content=f"Summary generation error: {e}")]}
    
    def run(self, input_message, thread_id):
        initial_state = {
            "messages": [HumanMessage(content=input_message)]
        }
        return self.state_graph.invoke(initial_state, config={"configurable": {"thread_id": thread_id}})
