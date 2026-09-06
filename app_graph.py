import json
import streamlit as st
from langchain_core.messages import HumanMessage
from agent_graph import research_graph

st.set_page_config(page_title="Agentic Researcher (LangGraph)", page_icon="🕸️", layout="wide")
st.title("Agentic Researcher (LangGraph)")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("E.g., Compare benchmark scores across top RAG papers..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        status_box = st.status("LangGraph executing...", expanded=True)
        final_answer = ""
        
        inputs = {"messages": [HumanMessage(content=prompt)]}
        
        for event in research_graph.stream(inputs, stream_mode="updates"):
            
            # 1. When the agent node decides to act
            if "agent" in event:
                message = event["agent"]["messages"][-1]
                
                if hasattr(message, "tool_calls") and message.tool_calls:
                    for tool_call in message.tool_calls:
                        tool_name = tool_call["name"]
                        tool_args = tool_call["args"]
                        status_box.write(f"🛠️ **Node: Agent** requested `{tool_name}`")
                        with status_box.expander(f"Tool Input: {tool_name}"):
                            st.json(tool_args)
                else:
                    final_answer = message.content

            # 2. When the tool node finishes executing
            elif "tools" in event:
                tool_messages = event["tools"]["messages"]
                for tool_msg in tool_messages:
                    tool_name = tool_msg.name
                    content = tool_msg.content
                    display_res = content[:1000] + "\n...[truncated]" if len(content) > 1000 else content
                    
                    status_box.write(f"⚙️ **Node: Tools** finished `{tool_name}`")
                    with status_box.expander(f"Tool Output: {tool_name}"):
                        st.text(display_res)

        status_box.update(label="Graph execution completed!", state="complete", expanded=False)
        st.markdown(final_answer)
        st.session_state.messages.append({"role": "assistant", "content": final_answer})