# How to Use: Apple Leadership Insights Agent

Welcome to the Apple Leadership Insights Agent! This guide will walk you through setting up, running, and using this AI-powered application to query Apple's FY24 and FY25 corporate documents.

---

## 1. Prerequisites and Setup

Before running the application, ensure you have the necessary dependencies and environment configured.

### Install Dependencies
Ensure you have Python 3 installed. Then, install the required packages using `pip`:
```bash
pip install -r requirements.txt
```

### Configure Environment Variables
The application relies on API keys to access language models (like Azure OpenAI, Google Gemini, Anthropic, or Minimax).
1. Locate the `.env.example` file in the root directory.
2. Create a copy of this file and name it `.env`.
3. Open `.env` and fill in your corresponding API keys. At a minimum, you must provide one valid API key (e.g., `AZURE_OPENAI_API_KEY` or `OPENAI_API_KEY`).

---

## 2. Setting Up the Knowledge Base (Data Ingestion)

The agent needs to read and index the corporate documents before it can answer questions.
1. Place your Apple SEC filings (PDFs) into the `data/` directory (e.g., `data/FISCAL_YEAR_2024/` and `data/FISCAL_YEAR_2025/`).
2. Run the ingestion pipeline to parse the PDFs, extract text and tables, perform OCR on images, and create the FAISS vector database.
```bash
python main.py --ingest
```
Wait for this process to complete. It will create a `db/` folder containing the FAISS index files.

---

## 3. Launching the Web Interface

Once the data is ingested, you can launch the interactive Streamlit chat interface.

1. Run the following command in your terminal:
```bash
streamlit run streamlit_app.py
```
2. A new tab should automatically open in your web browser pointing to `http://localhost:8501`.

---

## 4. Using the Chat Interface

### Navigating the UI
- **Main Chat Area**: This is where you type your questions and view the AI's responses.
- **Left Sidebar**: Contains information about the App, the Knowledge Base contents, and the LLM Configuration.

### Configuring Your AI Model
By default, the app uses Azure OpenAI (if configured in your `.env` file). You can change this on the fly:
1. Open the left sidebar.
2. Click the **"🤖 LLM Configuration"** expander to reveal the settings.
3. **Select Provider**: Choose from Azure OpenAI, OpenAI, Google Gemini, Anthropic, or Minimax.
4. **Enter Model Name**: You can specify the exact model ID you want to use (e.g., `gpt-4o`, `claude-3-5-sonnet-20240620`).
5. **API Key**: (Optional) You can temporarily override the API key here without modifying your `.env` file. If left blank, it falls back to your `.env` configuration.

### Asking Questions
1. At the bottom of the main area, locate the chat input box.
2. Type a question related to Apple's strategy or operations based on the ingested documents. Examples:
   - *"What were the key drivers for Services revenue growth in FY24?"*
   - *"How does Apple describe its supply chain risks in the latest 10-K?"*
   - *"Summarize the operational updates regarding the Vision Pro launch."*
3. Press **Enter**.

### Understanding the Responses
- **Text Answer**: The AI will provide a detailed, bulleted response based on the documents.
- **Visualizations (Charts)**: If the AI detects statistical, financial, or numerical data in the answer, it will automatically generate and display a beautiful interactive Plotly chart below the text.
- **Source Citations**: 
  - The text will include citation links (e.g., `[1]`, `[2]`).
  - Below the response, click the **"Source Details"** expander to see exactly which documents and excerpts the AI used to formulate its answer.

### Managing the Conversation
- Click the **"Clear Conversation"** button in the sidebar to reset the chat history and start fresh.

---

## 5. Pushing Updates to GitHub

If you make modifications to the code, you can push them using standard Git commands. Sensitive files like `.env`, the virtual environment (`.venv`), and local data/databases (`data/`, `db/`) are ignored by default.

```bash
git add .
git commit -m "Your commit message"
git push origin main
```
