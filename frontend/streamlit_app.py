# streamlit_app.py
import streamlit as st
import requests
import json
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Agentic AI Research Assistant",
    page_icon="🤖",
    layout="wide"
)

# Custom CSS (fix text color in boxes so text is visible)
st.markdown("""

<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .step-box {
        background-color: #e0f7fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
        border-left: 5px solid #00796b;
        color: #000;
    }
    .result-box {
        background: linear-gradient(135deg, #b2ebf2, #80deea);
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-top: 1rem;
        color: #000;
        font-weight: 500;
    }
</style>

""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🤖 Agentic AI Research Assistant</h1>', unsafe_allow_html=True)
st.markdown("### Powered by MCP + FastAPI + LangGraph")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    backend_url = st.secrets["BACKEND_URL"]
    max_iterations = st.slider("Max Iterations", 1, 10, 5)
    show_debug = st.checkbox("Show debug steps (internal)", value=False)

    st.markdown("---")
    st.markdown("### 📊 Status")

    # Health check
    try:
        response = requests.get(f"{backend_url}/health", timeout=2)
        if response.status_code == 200:
            st.success("✅ Backend Connected")
        else:
            st.error("❌ Backend Error")
    except:
        st.error("❌ Backend Offline")

    st.markdown("---")
    st.markdown("""
    ### 💡 How to use:
    1. Enter your research query
    2. Click 'Search & Analyze'
    3. Final answer will be shown. Enable debug steps to see internal steps.
    """)

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 🔍 Enter Your Query")
    query = st.text_area(
        "What would you like to research?",
        placeholder="e.g., Latest developments in quantum computing",
        height=100
    )

    search_button = st.button("🚀 Search & Analyze", type="primary")

with col2:
    st.markdown("### 📝 Quick Examples")
    examples = [
        "Latest AI trends 2024",
        "Climate change solutions",
        "Space exploration news",
        "Cryptocurrency updates"
    ]

    for example in examples:
        if st.button(example):
            query = example
            search_button = True

# Process query
if search_button and query:
    with st.spinner("🔄 Agent is working..."):
        try:
            # Call backend API
            response = requests.post(
                f"{backend_url}/query",
                json={
                    "query": query,
                    "max_iterations": max_iterations
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                # Display results
                st.markdown("## ✅ Final Answer")
                st.markdown(f'<div class="result-box">{data["result"]}</div>', unsafe_allow_html=True)

                # Optionally display internal steps if user asked for it
                if show_debug:
                    st.markdown("### 🔄 Internal Agent Steps (debug)")
                    for i, step in enumerate(data.get("steps", []), 1):
                        st.markdown(f'<div class="step-box"><strong>Step {i}:</strong> {step}</div>', unsafe_allow_html=True)

                # Metadata
                with st.expander("📋 Request Metadata"):
                    st.json({
                        "query": query,
                        "timestamp": datetime.now().isoformat(),
                        "steps_count": len(data.get("steps", [])),
                        "status": data.get("status", "")
                    })

                st.success("✅ Query processed successfully!")
            else:
                st.error(f"❌ Error: {response.status_code} - {response.text}")

        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The backend might be processing a complex query.")
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to backend. Make sure the FastAPI server is running.")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Query history
if "history" not in st.session_state:
    st.session_state.history = []

if search_button and query:
    st.session_state.history.append({
        "query": query,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

# Display history
if st.session_state.history:
    with st.expander("📜 Query History"):
        for item in reversed(st.session_state.history[-5:]):
            st.markdown(f"**{item['timestamp']}** - {item['query']}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Built with ❤️ using FastAPI, LangGraph, MCP & Streamlit</p>
</div>
""", unsafe_allow_html=True)
