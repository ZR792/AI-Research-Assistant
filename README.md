# 🤖 Agentic AI Research Assistant

An intelligent, multi-component AI system designed to autonomously perform research, analysis, and report generation using a modern agentic architecture.

## 📋 Project Overview

This project implements a complete, production-ready **Agentic AI Research Assistant** leveraging the **Model Context Protocol (MCP)** for robust tool integration. The system is designed with a clear separation of concerns, utilizing a high-performance **FastAPI** backend for the core logic and a responsive **Streamlit** application for the user interface.

### 🌟 Key Technologies

| Technology | Role |
| :--- | :--- |
| **FastAPI** | High-performance Python web framework for scalable API services (Backend) |
| **LangGraph** | Framework for building agentic, multi-step reasoning and stateful workflows |
| **MCP** | Model Context Protocol for structured tool/function integration (Core Agent) |
| **Streamlit** | Fast and intuitive UI development for Python web applications (Frontend) |
| **Uvicorn** | ASGI server used to run the FastAPI backend |

---

## 🎨 Features

* **Agentic Reasoning:** Uses **LangGraph** to orchestrate complex, multi-step workflows for thorough research and analysis.
* **MCP Integration:** Implements the **Model Context Protocol** standard for seamless and reliable tool calling (e.g., for web search).
* **Real-time Search:** Fetches live, up-to-date information from the web to ensure report accuracy.
* **Beautiful UI:** Modern, responsive **Streamlit** interface for user interaction, query history, and real-time feedback.
* **Health Monitoring:** Includes a backend health check feature within the UI sidebar.
* **Decoupled Architecture:** Separates the UI and API logic for independent scaling and maintenance. 

---
## 📁 Complete File Structure

The project is split into `backend/` (API/Agent services) and `frontend/` (Streamlit UI).

````
agentic-ai-project/
├── backend/
│   ├── app.py              # FastAPI server
│   ├── agent.py            # LangGraph agent
│   ├── mcp_server.py       # MCP tools
│   └── requirements.txt    # Backend dependencies
├── frontend/
│   ├── streamlit_app.py    # Streamlit UI
│   └── requirements.txt    # Frontend dependencies
└── README.md               # This file
````
---


## ⚙️ Setup and Running the Application

Follow these steps to set up and run the research assistant locally.

### 1. Create and Structure the Project


1. Create the main directory
```bash
mkdir Final_Project
cd Final_Project
````
2. Create the backend and frontend subdirectories
```bash
mkdir backend frontend
```
3. Set Up the Backend
Place app.py, agent.py, mcp_server.py, and requirements.txt inside the backend/ folder.

Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

4. Set Up the Frontend
Place streamlit_app.py and requirements.txt inside the frontend/ folder.

Install dependencies:
```bash
cd ../frontend
pip install -r requirements.txt
```

5. ▶️ Running the Application
The application requires two separate terminal sessions to run the decoupled services.

Step 5.1: Start the Backend API (Terminal 1)
The FastAPI server provides the research endpoint and orchestrates the agent.
``
cd ../backend
``
# Assuming app.py is configured to run with Uvicorn
```bash
python app.py
```
Step 5.2: Start the Frontend UI (Terminal 2)
``
streamlit run frontend/streamlit_app.py
``
The Streamlit application will connect to the running backend service.

