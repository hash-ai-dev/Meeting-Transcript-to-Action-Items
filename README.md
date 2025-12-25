# Meeting Action Extractor

## Prerequisites
-   **Python 3.8+**
-   **Ollama**: Required for the LLM agent.
    -   Install Ollama from [ollama.com](https://ollama.com).
    -   Pull the required model: `ollama pull llama3.2`

## Setup
1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Backend
1.  Start the Flask server:
    ```bash
    python backend/app.py
    ```
2.  The server will run on `http://127.0.0.1:5000`.

## Architecture
## Architecture
-   **Backend**: Flask (handling text processing and deep LLM analysis).
-   **Frontend**: Streamlit (Chat-like interface).
-   **LLM**: Ollama (`llama3.2`) for key extraction (Action Items vs Notes).
