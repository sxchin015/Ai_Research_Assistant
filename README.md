<div align="center">

<img src="https://img.shields.io/badge/🔬_AI_Research_Assistant-v1.0-a78bfa?style=for-the-badge" />

# AI Research Assistant Chatbot

### A smart chatbot that reads your documents + searches the web using 100% free AI

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3.3_70B-F55036?style=flat-square)](https://console.groq.com)
[![Cost](https://img.shields.io/badge/Total_Cost-$0_Free-22c55e?style=flat-square)](#)

**Built for NeoStats AI Engineer Assignment by [sxchin015](https://github.com/sxchin015)**

</div>

---

## 🤔 What Does This Do?

Most AI chatbots don't know what's in your PDF files, and their knowledge becomes outdated. This project fixes both:

| Problem | Solution |
|---|---|
| "My chatbot doesn't know what's in my PDF" | Upload any PDF/TXT → the bot reads it and answers from it |
| "The AI's knowledge is outdated" | Automatically searches the web when the doc doesn't have the answer |
| "I need short answers sometimes, deep answers other times" | Toggle between **Concise** (2-3 lines) and **Detailed** (full explanation) mode |
| "I can't afford paid AI APIs" | Runs entirely on **free tools** — no credit card ever |

---

## 💸 Total Cost: $0

| What | Tool | Cost |
|---|---|---|
| 🤖 AI Brain | Groq — LLaMA 3.3 70B | **Free** |
| 🧠 Text Understanding | sentence-transformers (runs on your PC) | **Free** |
| 🌐 Web Search | DuckDuckGo | **Free** |
| 📦 Document Search | FAISS vector store (runs locally) | **Free** |
| 🖥️ User Interface | Streamlit | **Free** |
| ☁️ Cloud Hosting | Streamlit Cloud | **Free** |

---

## 📁 Project Structure

```
Ai_Research_Assistant/
│
├── 📄 app.py                        ← Run this to start the chatbot
│
├── ⚙️  config/
│   └── config.py                    ← All settings (reads from .env file)
│
├── 🤖 models/
│   ├── llm.py                       ← Connects to Groq AI + streams answers
│   └── embeddings.py                ← Converts text to numbers locally (no API)
│
├── 🛠️  utils/
│   ├── rag_utils.py                 ← Reads PDF → splits → searches → retrieves
│   └── web_search.py                ← DuckDuckGo search fallback
│
├── 📋 requirements.txt              ← Python packages to install
├── 🔑 .env.example                  ← Copy this to .env and add your key
├── 🚫 .gitignore                    ← Keeps secrets off GitHub
└── 📊 AI_Research_Assistant_Presentation.pptx
```

---

## 🚀 Getting Started

### Step 1 — Get your FREE Groq API Key

> Takes 2 minutes. No credit card. No phone number. Just your email.

1. Go to **[https://console.groq.com](https://console.groq.com)**
2. Click **"Sign Up"** → enter your email → verify it
3. After login → click **"API Keys"** in the left sidebar
4. Click **"Create API Key"** → copy the key (it starts with `gsk_...`)

---

### Step 2 — Download & Set Up the Project

```bash
# Clone the repo
git clone https://github.com/sxchin015/Ai_Research_Assistant.git
cd Ai_Research_Assistant

# Create a virtual environment (keeps things clean)
python -m venv venv

# Activate it
source venv/bin/activate        # Mac / Linux
venv\Scripts\activate           # Windows

# Install all required packages
pip install -r requirements.txt
```

> ⏳ First install takes 2-3 minutes — it downloads the AI embedding model (~90MB). This only happens once.

---

### Step 3 — Add Your API Key

```bash
# Copy the example file
cp .env.example .env
```

Now open the `.env` file in any text editor and replace the placeholder:

```env
GROQ_API_KEY=gsk_paste_your_actual_key_here
```

Save the file. That's it — no other changes needed.

---

### Step 4 — Run the App

```bash
streamlit run app.py
```

Your browser will open automatically at **[http://localhost:8501](http://localhost:8501)** ✅

> 💡 If your browser doesn't open, manually go to `http://localhost:8501`

---

## 🎯 How to Use the App

### Chatting without a document
Just type any question in the chat box at the bottom. The bot will search the web and answer using Groq AI.

### Chatting with your own document
1. Look at the **left sidebar** → find **"Upload Document (RAG)"**
2. Click **"Browse files"** → select your PDF or TXT file
3. Wait for the green tick: **✅ Indexed X chunks from yourfile.pdf**
4. Now type questions about your document — the bot will search it first

### Reading the source badges
Every answer tells you exactly where the information came from:

| Badge | Meaning |
|---|---|
| 🟢 **RAG · Document** | Answer found inside your uploaded file |
| 🔵 **Web · DuckDuckGo** | Answer found by searching the internet |
| 🟣 **Groq LLaMA** | Answer from the AI's own training knowledge |

### Switching response depth
In the sidebar under **"Response Mode"**:
- **Concise** → 2-3 sentence answer, straight to the point
- **Detailed** → Full explanation with headings and examples

---

## 🔄 How It Works (Simple Explanation)

```
You type a question
         │
         ▼
 ┌───────────────────┐
 │  Did you upload   │
 │   a document?     │
 └──────┬────────────┘
        │
   YES  │                          NO
        ▼                           │
 Search the PDF using               │
 vector similarity (FAISS)          │
        │                           │
  Found something?                  │
   YES ──────────────────────┐      │
   NO  ──────────────────────┼──────┘
                             │
                             ▼
                    Search DuckDuckGo
                    for live web results
                             │
                             ▼
                  Send results + question
                    to Groq LLaMA AI
                             │
                             ▼
                  Answer streams word
                  by word to your screen
```

**The document search process:**
- Your PDF gets read and split into 800-character pieces
- Each piece is converted into a list of numbers (called an "embedding")
- These numbers are stored in a FAISS index on your computer
- When you ask a question, it also gets converted to numbers
- FAISS finds the pieces with the most similar numbers
- Those pieces are given to Groq as context

---

## ☁️ Deploy to Streamlit Cloud (Free, ~2 minutes)

### Step 1 — Make sure your code is on GitHub
```bash
git add .
git commit -m "Add AI Research Assistant"
git push origin main
```

### Step 2 — Deploy
1. Go to **[https://streamlit.io/cloud](https://streamlit.io/cloud)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Fill in:
   - **Repository:** `sxchin015/Ai_Research_Assistant`
   - **Branch:** `main`
   - **Main file path:** `app.py`
5. Click **"Advanced settings"** → **"Secrets"**
6. Paste this (with your real key):
   ```toml
   GROQ_API_KEY = "gsk_your_actual_key_here"
   ```
7. Click **"Deploy"**

Your app will be live at `https://your-app-name.streamlit.app` 🎉

---

## ⚙️ Configuration Options

Open your `.env` file to change these settings:

```env
# Required
GROQ_API_KEY=gsk_...

# Change the AI model (all free on Groq)
GROQ_MODEL=llama-3.3-70b-versatile

# Change the embedding model (runs locally)
EMBEDDING_MODEL=all-MiniLM-L6-v2

# RAG settings (advanced - usually no need to change)
CHUNK_SIZE=800          # characters per document chunk
CHUNK_OVERLAP=100       # overlap between chunks
TOP_K_RESULTS=4         # how many chunks to retrieve
MIN_RELEVANCE_SCORE=0.30  # minimum match score (0-1)
```

### Available Groq Models (all free)

| Model | Speed | Best For |
|---|---|---|
| `llama-3.3-70b-versatile` | ⚡ Fast | **Default — best quality** |
| `llama-3.1-8b-instant` | 🚀 Fastest | Quick answers |
| `mixtral-8x7b-32768` | 📄 Medium | Very long documents |
| `gemma2-9b-it` | 🎯 Balanced | General use |

---

## ❗ Common Errors & Fixes

| Error Message | What It Means | How to Fix |
|---|---|---|
| `Invalid API Key` | Wrong or expired Groq key | Copy a fresh key from [console.groq.com](https://console.groq.com) and paste in sidebar |
| `model_decommissioned` | Using an old model name | Change `GROQ_MODEL` to `llama-3.3-70b-versatile` in `.env` |
| Indexing stuck on first upload | Downloading embedding model (~90MB) | Wait 2-3 minutes — only happens once ever |
| `faiss-cpu not installed` | Missing package | Run `pip install faiss-cpu` |
| `duckduckgo-search` rate limit | Too many searches | Wait 30 seconds and try again |
| App shows blank screen | Streamlit not started | Run `streamlit run app.py` in your terminal |

---

## 🧱 Full Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.9+ |
| UI Framework | Streamlit | 1.35+ |
| LLM | Groq API (LLaMA 3.3 70B) | Latest |
| Local Embeddings | sentence-transformers | 3.0+ |
| Embedding Model | all-MiniLM-L6-v2 | - |
| Vector Store | FAISS-CPU | 1.7+ |
| PDF Parser | pdfplumber | 0.11+ |
| Web Search | duckduckgo-search | 6.1+ |
| Config Manager | python-dotenv | 1.0+ |

---

## 👤 Author

**Sachin** — [@sxchin015](https://github.com/sxchin015)

Built for the **NeoStats AI Engineer Assignment 2026**

---

<div align="center">

Made with ❤️ &nbsp;|&nbsp; Powered by [Groq](https://console.groq.com) &nbsp;|&nbsp; Total cost: **$0**

⭐ Star this repo if it helped you!

</div>
