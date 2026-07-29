# Local AI Workspace 

A powerful, privacy-first, locally-hosted AI assistant with a beautiful web interface. Powered by **Ollama**, **FastAPI**, and the **Model Context Protocol (MCP)**.

Instead of a standard chatbot that is trapped in a browser tab, this workspace gives a local Large Language Model (like Llama 3.1) secure, agentic access to your real-world data and applications.

##  Key Features

*   **100% Local Inference**: The "brain" of the AI runs on your own hardware using Ollama. No prompts or personal data are sent to cloud AI providers.
*   **Agentic Framework**: The orchestrator allows the AI to autonomously plan tasks, decide which tools to use, execute them, and parse the results in a loop.
*   **Ultra-Premium Web UI**: A beautiful, modern "Dark Aurora" web interface built with glassmorphism, smooth animations, and a dynamic integrations dashboard.
*   **Isolated MCP Plugin Architecture**: Every tool runs in its own isolated Python sub-process using the Model Context Protocol. If one API crashes, the rest of the workspace remains perfectly stable.

---

##  Included Integrations (MCP Servers)

The workspace currently supports a massive suite of real-world tools:

*   **Google Workspace Suite:**
    *    **Gmail:** Read and send emails.
    *    **Calendar:** Check your schedule and create new events.
    *    **Drive:** Search and manage files.
    *    **Docs:** Read and create documents.
    *    **Meet:** Generate instant video call links.
*   **Developer & Web Tools:**
    *    **GitHub:** Search repositories and read user profiles.
    *    **DuckDuckGo:** Fetch live web search results.
*   **Media:**
    *    **YouTube:** Search for videos and fetch links.
    *    **Spotify:** Control music playback and search tracks *(Requires Spotify Premium)*.

*(Note: The MCP architecture makes it incredibly easy to add new tools. Just create a new `server.py` in the `tools/` directory and register it!)*

---

##  Architecture

1.  **Frontend (`frontend/`)**: HTML/CSS/JS interface that sends user queries via HTTP POST to the backend.
2.  **API Backend (`api.py`)**: A FastAPI server that routes requests and manages the Orchestrator's lifespan.
3.  **Orchestrator (`core/orchestrator.py`)**: The central loop that passes context between the LLM and the Tool Registry.
4.  **Tool Registry (`registry/tool_registry.py`)**: Spawns and communicates with the isolated MCP tool servers over `stdio`.
5.  **Ollama Client (`ollama/client.py`)**: An asynchronous client to communicate with your local Ollama instance.

---

##  Setup & Installation

### 1. Prerequisites
*   Install [Ollama](https://ollama.com/) and have it running in the background.
*   Pull a model (e.g., `ollama pull llama3.1`).
*   Python 3.10+ installed.

### 2. Environment Setup
```bash
# Clone the repo and install dependencies
pip install -r requirements.txt

# Set up your environment variables
cp .env.example .env
```

### 3. API Credentials
For the Google, GitHub, and Spotify tools to work, you must provide your own API credentials:
*   **Google Tools:** Download your OAuth 2.0 Client credentials from the Google Cloud Console and place them in the respective folders (e.g., `tools/gmail/credentials.json`, `tools/calendar/credentials.json`).
*   **GitHub/Spotify:** Add your API tokens to your `.env` file.

*Run the individual `auth.py` scripts inside the tool folders (like `tools/spotify/auth.py`) once to cache your login tokens!*

### 4. Run the Workspace
Instead of running a basic python script, start the FastAPI web server:

```bash
python -m uvicorn api:app --reload
```

Open your web browser and navigate to **`http://localhost:8000`** to start chatting with your Local AI Workspace!
