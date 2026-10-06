import streamlit as st
from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent

# Import the MCP tools we built in Step 2
from server import get_database_schema, execute_read_query

# --- PAGE SETUP & THEME ---
st.set_page_config(page_title="AI Data Analyst", page_icon="📊", layout="wide")

# --- CSS THEMES ---
DARK_CSS = """
<style>
.stApp { background-color: #0a0a0a; }
h1, h2, h3, p, span, .stMarkdown { color: #ffffff !important; }
[data-testid="stSidebar"] { background-color: #121212; border-right: 1px solid #333; }
.stChatMessage:nth-child(even) { background-color: #1a1a1a; color: #ffffff; border-radius: 10px; padding: 15px; border-left: 4px solid #00e5ff; border: 1px solid #333; }
.stChatMessage:nth-child(odd) { background-color: #1a1a1a; color: #ffffff; border-radius: 10px; padding: 15px; border-left: 4px solid #b388ff; border: 1px solid #333; box-shadow: 0px 4px 12px rgba(179, 136, 255, 0.15); }
div.stButton > button { background-color: #ffffff !important; color: #000000 !important; border: 2px solid #ffffff !important; border-radius: 8px !important; font-weight: bold !important; padding: 10px 24px !important; transition: all 0.3s ease; }
div.stButton > button:hover { background: linear-gradient(135deg, #00e5ff 0%, #b388ff 100%) !important; color: white !important; border: 2px solid transparent !important; transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0, 229, 255, 0.3); }
.stChatInputContainer textarea { background-color: #121212 !important; color: #ffffff !important; border: 1px solid #444 !important; }
header {visibility: hidden;}
</style>
"""

LIGHT_CSS = """
<style>
.stApp { background-color: #f8f9fa; }
h1, h2, h3, p, span, .stMarkdown { color: #212529 !important; }
[data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #dee2e6; }
.stChatMessage:nth-child(even) { background-color: #e3f2fd; border-radius: 10px; padding: 15px; border-left: 5px solid #1976d2; color: #212529; }
.stChatMessage:nth-child(odd) { background-color: #ffffff; border-radius: 10px; padding: 15px; border-left: 5px solid #2e7d32; box-shadow: 0px 2px 5px rgba(0,0,0,0.05); color: #212529; }
div.stButton > button { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important; color: white !important; border: none !important; border-radius: 8px !important; font-weight: bold !important; padding: 10px 24px !important; transition: all 0.3s ease; }
div.stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(118, 75, 162, 0.4); color: white !important; }
.stChatInputContainer textarea { background-color: #ffffff !important; color: #212529 !important; border: 1px solid #ced4da !important; }
header {visibility: hidden;}
</style>
"""

# --- SIDEBAR & THEME TOGGLE ---
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    # The new theme toggle button!
    is_dark_mode = st.toggle("🌙 Dark Theme", value=True)
    
    st.markdown("---")
    st.success("✅ Secure Connection Active")
    st.markdown("This AI agent connects directly to your SQL database using the Model Context Protocol (MCP).")
    st.markdown("---")
    
    # Clear Chat Button
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = [

            {"role": "assistant", "content": "Hello! I am your AI Data Analyst. Try asking: **'What are our top 3 best-selling products?'**"}
        ]
        st.rerun()

# Apply chosen theme
if is_dark_mode:
    st.markdown(DARK_CSS, unsafe_allow_html=True)
else:
    st.markdown(LIGHT_CSS, unsafe_allow_html=True)

# --- HEADER ---
st.title("📊 AI Data Analyst Copilot")
st.markdown("💬 **Chat with your SQL Database in Plain English!**")
st.divider()

# --- SECURE API KEY HANDLING ---
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    st.error("🚨 **API Key Missing!** Please add your Groq API Key to `.streamlit/secrets.toml` to continue.")
    st.stop()

# --- LANGCHAIN TOOLS ---
@tool
def schema_tool() -> str:
    """Use this tool FIRST to get the database schema (tables and columns) before writing any SQL."""
    return get_database_schema()

@tool
def query_tool(query: str) -> str:
    """Use this tool to execute a SELECT SQL query and get the actual data from the database."""
    return execute_read_query(query)

tools = [schema_tool, query_tool]

# --- CHAT UI & SESSION STATE ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello! I am your AI Data Analyst. Try asking: **'What are our top 3 best-selling products?'**"}
    ]

# Display chat messages
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- AGENT EXECUTION ---
if prompt := st.chat_input("E.g., How many users signed up?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Initialize LLM and LangGraph Agent
    llm = ChatGroq(api_key=api_key, model="openai/gpt-oss-120b", temperature=0)
    
    system_prompt = (
        "You are a friendly and intelligent AI Data Analyst. "
        "1. If the user asks basic conversational questions (like 'Hello', 'Who are you?', or 'What can you do?'), just reply normally and nicely. DO NOT use any tools for these questions. "
        "2. If the user asks about data (e.g., users, orders, products, sales), you MUST use the schema_tool to find the tables, then use the query_tool to run a SQL SELECT query to get the answer."
    )
    agent = create_react_agent(llm, tools)

    with st.spinner("🧠 AI is analyzing database schema and executing SQL..."):
        try:
            # Pass the system instructions directly in the messages array
            response = agent.invoke({"messages": [("system", system_prompt), ("user", prompt)]})
            output = response["messages"][-1].content
            
            st.session_state.messages.append({"role": "assistant", "content": output})
            st.chat_message("assistant").write(output)
        except Exception as e:
            st.error(f"An error occurred: {e}")