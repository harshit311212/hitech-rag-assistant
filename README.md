# ⚖️ Bits and RAGs on HITECH

**A cinematic, dark-themed Legal Retrieval-Augmented Generation (RAG) assistant specifically designed to query and cite the HITECH Act (Public Law 111-5, Privacy & Security Subtitles).**

This application allows users to ask complex legal questions about healthcare privacy, breach notifications, and vendor obligations. It retrieves verbatim sections from the actual legal document and uses Groq's fast LLM inference to generate strictly-grounded answers.

---

## 🎨 Design & UI
The interface was built following a strict **"Cinematic Cave Moonlight"** aesthetic:
- **Color Palette:** Deep forest primary background (`#09100B`), soft emerald secondary panels (`#265131`), and striking neon green accents (`#51C445`).
- **Typography:** Uses Google's `Inter` for clean readability and `JetBrains Mono` for metadata and status badges.
- **Glassmorphism:** AI chat bubbles and citation cards use semi-transparent backgrounds with background blur for a premium, modern feel.
- **Floating Citations:** Retrieved document chunks are displayed as interactive cards below the AI response, complete with relevance match percentages and page numbers.

---

## 🛠️ Tech Stack & Architecture

### **Core Pipeline**
*   **Framework:** [LangChain](https://python.langchain.com/) (Document loading, text splitting, retrieval chains)
*   **LLM Inference:** [Groq API](https://groq.com/) using `llama-3.3-70b-versatile` for near-instant text generation.
*   **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2` (Running completely locally via HuggingFace for privacy and speed).
*   **Vector Database:** [FAISS](https://faiss.ai/) (Facebook AI Similarity Search) used for local, persistent vector storage (`./faiss_index/`).

### **Security & Grounding**
*   **Strict RAG Prompting:** The system prompt is hardened against prompt injections, hallucination, and general-knowledge queries. The model is forced to refuse answers that are not explicitly found in the retrieved chunks.
*   **XSS Protection:** All user inputs and AI outputs are strictly HTML-escaped before rendering in the custom Streamlit UI.

---

## 🚀 Running Locally

### 1. Requirements
Ensure you have Python 3.9+ installed.
```bash
git clone https://github.com/harshit311212/hitech-rag-assistant.git
cd hitech-rag-assistant
pip install -r requirements.txt
```

### 2. API Key Setup
The application requires a free Groq API key to run the LLM. 
Get one at: [console.groq.com](https://console.groq.com)

Create a `.env` file in the root directory:
```env
GROQ_API_KEY=gsk_your_api_key_here
```

### 3. Start the App
```bash
streamlit run app.py
```
*(The FAISS vector index will be automatically built from the `hitech-pub-l-111-5_0.pdf` document upon your very first query).*

---

## ☁️ Deploying to Streamlit Community Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/)
2. Click **Create app** -> **Use existing repo**.
3. Select this repository branch and set the Main file path to `app.py`.
4. Click **Advanced settings...** and add your Groq API key to the **Secrets** block:
   ```toml
   GROQ_API_KEY = "gsk_your_api_key_here"
   ```
5. Click **Deploy!**
