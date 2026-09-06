import streamlit as st
from agent import run_agent

st.set_page_config(page_title="Agentic RAG Researcher", page_icon="🧠", layout="wide")
st.title("Agentic Researcher")
st.markdown("An AI Agent utilizing Web Fetch, arXiv Search, Tavily, and E2B Sandboxed Python Execution.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("E.g., Compare recent agentic RAG benchmarks..."):
    
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        
        status_box = st.status("Agent is thinking...", expanded=True)
        answer_placeholder = st.empty()
        final_answer = ""
        
        for update in run_agent(prompt):
            
            if update["type"] == "status":
                status_box.write(f"🔄 **{update['content']}**")
                
            elif update["type"] == "tool_start":
                tool_name = update["tool_name"]
                args = update["args"]
                status_box.write(f"🛠️ **Executing:** `{tool_name}`")
                
                with status_box.expander(f"Input: {tool_name}"):
                    st.code(args, language="json")
                    
            elif update["type"] == "tool_end":
                tool_name = update["tool_name"]
                result = update["result"]
                
                display_result = result[:1000] + "\n...[truncated for display]" if len(result) > 1000 else result
                
                with status_box.expander(f"Output: {tool_name}"):
                    st.text(display_result)
                    
            elif update["type"] == "final_answer":
                status_box.update(label="Analysis complete!", state="complete", expanded=False)
                final_answer = update["content"]
                answer_placeholder.markdown(final_answer)
                
            elif update["type"] == "error":
                status_box.update(label="An error occurred.", state="error", expanded=True)
                st.error(update["content"])
                
        if final_answer:
            st.session_state.messages.append({"role": "assistant", "content": final_answer})