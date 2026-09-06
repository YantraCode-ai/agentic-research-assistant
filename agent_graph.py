from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from config import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
from prompts import SYSTEM_PROMPT
from tools_langchain import TOOLS
import logging

logger = logging.getLogger(__name__)

MAX_STEPS = 10
TOOL_BUDGET = 4 

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    step_count: int
    tool_call_count: int

llm = ChatOpenAI(
    model=MODEL_NAME,
    openai_api_key=OPENROUTER_API_KEY,
    openai_api_base=OPENROUTER_BASE_URL,
    temperature=0.2,
)
model_with_tools = llm.bind_tools(TOOLS)
model_no_tools = llm  

def call_model(state: AgentState):
    messages = state["messages"]
    if not messages or not isinstance(messages[0], SystemMessage):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages

    step_count = state.get("step_count", 0) + 1
    tool_call_count = state.get("tool_call_count", 0)
    budget_exhausted = tool_call_count >= TOOL_BUDGET
    near_limit = step_count >= MAX_STEPS - 1

    try:
        if budget_exhausted or near_limit:
            nudge = HumanMessage(
                content="You have gathered sufficient data. Produce your final, "
                        "comprehensive answer now — do not call any more tools."
            )
            response = model_no_tools.invoke(messages + [nudge])
        else:
            response = model_with_tools.invoke(messages)
    except Exception:
        logger.exception("LLM call failed at step %d", step_count)
        response = AIMessage(content="I ran into an error while processing this request.")

    new_tool_calls = len(getattr(response, "tool_calls", None) or [])
    return {
        "messages": [response],
        "step_count": step_count,
        "tool_call_count": tool_call_count + new_tool_calls,
    }

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "tools"
    return END

workflow = StateGraph(AgentState)
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(TOOLS))
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
workflow.add_edge("tools", "agent")

research_graph = workflow.compile()