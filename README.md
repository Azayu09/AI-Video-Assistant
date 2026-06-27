# 🎬 AI Video Assistant

An AI-powered Meeting & Video Assistant that transforms YouTube videos or uploaded audio/video files into structured meeting insights using **Local Whisper**, **LangChain LCEL**, **Mistral AI**, **ChromaDB**, and **Streamlit**.

The application automatically transcribes meetings, generates concise summaries, extracts action items and key decisions, and enables users to chat with meeting transcripts using Retrieval-Augmented Generation (RAG).

---

# 🚀 Features

* 🎥 Supports YouTube URLs and local audio/video files
* 🎙️ Local Whisper speech-to-text transcription
* 🌐 Hindi/Hinglish → English transcription using Sarvam AI
* 📝 AI-generated meeting summaries
* ✅ Automatic Action Item extraction
* 🔑 Key Decision extraction
* ❓ Open Question detection
* 🧠 Chat with meeting transcripts using RAG
* 📚 ChromaDB vector database
* 🔍 Semantic search over transcripts
* 📄 Export reports as PDF
* 🎨 Modern dark-themed Streamlit UI

---

# 🛠 Tech Stack

### Frontend

* Streamlit
* HTML
* CSS

### Backend

* Python

### AI / Machine Learning

* OpenAI Whisper
* Mistral AI
* LangChain LCEL
* HuggingFace Sentence Transformers

### RAG

* ChromaDB
* LangChain Retriever

### Translation

* Sarvam AI

### Other Libraries

* yt-dlp
* ffmpeg
* pydub
* PyTorch
* Transformers
* fpdf2

---

# 🏗 System Architecture

```text
YouTube URL / Local File
            │
            ▼
     Audio Extraction
            │
            ▼
 Local Whisper Transcription
            │
            ▼
 Hindi/Hinglish Translation
      (Sarvam AI)
            │
            ▼
   Meeting Transcript
            │
            ▼
   Recursive Text Splitter
            │
            ▼
 Sentence Embeddings
            │
            ▼
     Chroma Vector DB
            │
            ▼
   LangChain LCEL Pipeline
            │
      ┌─────┴───────────┐
      ▼                 ▼
Meeting Summary      RAG Chat
      │
      ▼
Action Items
Key Decisions
Open Questions
```

---

# 📂 Project Structure

```text
AI-Video-Assistant/
│
├── app.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
│
├── core/
│   ├── extractor.py
│   ├── rag_engine.py
│   ├── summarizer.py
│   ├── transcriber.py
│   └── vector_store.py
│
├── utils/
│   └── audio_processor.py
│
├── assets/
│   ├── landing.png
│   ├── processing.png
│   ├── summary.png
│   └── chat.png
│
└── vector_db/
```

---

# ⚙️ Installation

## 1. Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/AI-Video-Assistant.git

cd AI-Video-Assistant
```

---

## 2. Create Virtual Environment

Using UV

```bash
uv venv
```

or

```bash
python -m venv .venv
```

---

## 3. Activate Environment

### Windows

```bash
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

---

## 4. Install Dependencies

Using UV

```bash
uv pip install -r requirements.txt
```

or

```bash
pip install -r requirements.txt
```

---

## 5. Install FFmpeg

Download FFmpeg from

https://ffmpeg.org/download.html

Add the FFmpeg `bin` folder to your system PATH.

Verify installation:

```bash
ffmpeg -version
```

---

## 6. Configure Environment Variables

Create a `.env` file in the project root.

```env
MISTRAL_API_KEY=your_mistral_api_key

SARVAM_API_KEY=your_sarvam_api_key

WHISPER_MODEL=small
```

---

## 7. Run the Application

```bash
streamlit run app.py
```

---

# 💡 Usage

1. Launch the application.
2. Paste a YouTube URL or provide a local file path.
3. Select the meeting language.
4. Click **Analyse**.
5. Wait for the transcription and processing pipeline to complete.
6. Review:

   * Meeting Title
   * Summary
   * Action Items
   * Key Decisions
   * Open Questions
7. Ask questions about the meeting using the built-in AI chat.
8. Export the report as a PDF.

---

# 📌 Example Questions

* What are the key decisions made?
* What action items were assigned?
* Who is responsible for the deployment?
* Summarize the discussion in five points.
* What deadlines were mentioned?
* What were the risks discussed?

---

# 🔍 Features Explained

### 🎙 Whisper Transcription

Uses OpenAI Whisper locally for fast and accurate speech recognition.

---

### 🌐 Hindi/Hinglish Translation

Automatically converts Hindi/Hinglish meetings into English using Sarvam AI.

---

### 📝 AI Summarization

Uses Mistral AI with LangChain LCEL to create concise meeting summaries.

---

### 📚 Retrieval-Augmented Generation (RAG)

Meeting transcripts are split into chunks, embedded using HuggingFace embeddings, stored in ChromaDB, and retrieved using semantic search for context-aware question answering.

---

### 📄 PDF Export

Generate professional meeting reports containing:

* Meeting Title
* Summary
* Action Items
* Key Decisions
* Open Questions
* Full Transcript

---

# 🧠 AI Pipeline

```
Audio
   │
   ▼
Whisper
   │
   ▼
Translation
   │
   ▼
Transcript
   │
   ▼
Chunking
   │
   ▼
Embeddings
   │
   ▼
Vector Database
   │
   ▼
Retriever
   │
   ▼
Mistral AI
   │
   ▼
Answer / Summary
```

---

# 📦 Dependencies

* Streamlit
* LangChain
* ChromaDB
* OpenAI Whisper
* PyTorch
* HuggingFace Sentence Transformers
* yt-dlp
* ffmpeg
* pydub
* Mistral AI
* Sarvam AI

---

# 🔮 Future Improvements

* Speaker Diarization
* Live Meeting Support
* Meeting Timeline
* Speaker-wise Summaries
* Cloud Storage Integration
* Google Drive Integration
* Calendar Integration
* Meeting Analytics Dashboard
* Team Collaboration
* Email Summary Automation
* Mobile-Friendly UI
* Multi-language Support

---

# 🤝 Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a new branch.
3. Commit your changes.
4. Push the branch.
5. Open a Pull Request.

---

# ⭐ Support

If you found this project useful:

* ⭐ Star the repository
* 🍴 Fork the project
* 🐞 Report issues
* 💡 Suggest new features

Every star helps the project reach more developers. The algorithm, like most algorithms, craves attention.
