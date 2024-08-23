from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END, MessagesState
import datetime
from tools import book_appointment, get_next_available_appointment, cancel_appointment
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage

llm = ChatOpenAI(model='gpt-4o')

CONVERSATION = []

# Invoke model
def receive_message_from_caller(message):
    CONVERSATION.append(HumanMessage(content=message, type="human"))
    state = {
        "messages": CONVERSATION,
    }
    print(state)
    new_state = caller_app.invoke(state)
    CONVERSATION.extend(new_state["messages"][len(CONVERSATION):])


# Edges
def should_continue_caller(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "continue"


# Nodes
def call_caller_model(state: MessagesState):
    state["current_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    response = caller_model.invoke(state)
    return {"messages": [response]}


caller_tools = [book_appointment, get_next_available_appointment, cancel_appointment]
tool_node = ToolNode(caller_tools)


caller_pa_prompt = """You are a personal assistant, and need to help the user to book or cancel appointments, you should check the available appointments before booking anything. Be extremely polite, so much so that it is almost rude.
Current time: {current_time}
"""

caller_chat_template = ChatPromptTemplate.from_messages([
    ("system", caller_pa_prompt),
    ("placeholder", "{messages}"),
])

caller_model = caller_chat_template | llm.bind_tools(caller_tools)



# Graph 
caller_workflow = StateGraph(MessagesState)

# Add Nodes
caller_workflow.add_node("agent", call_caller_model)
caller_workflow.add_node("action", tool_node)

# Add Edges
caller_workflow.add_conditional_edges(
    "agent",
    should_continue_caller,
    {
        "continue": "action",
        "end": END,
    },
)
caller_workflow.add_edge("action", "agent")

# Set Entry Point and build the graph
caller_workflow.set_entry_point("agent")

caller_app = caller_workflow.compile()
