# 🤖 AI PDF Reader

An intelligent PDF question-answering system powered by local AI models. Upload PDFs and ask questions about their content - completely free, private, and running 100% on your machine.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 📄 **Multi-PDF Support** - Upload and process multiple documents simultaneously
- 💬 **Conversational Interface** - Natural chat-based interaction with your documents
- 🤖 **Multiple AI Models** - Choose between llama3 and gemma3 for speed vs quality
- 🔒 **100% Private** - Everything runs locally on your machine
- 💰 **Completely Free** - No API costs or subscriptions required
- 📊 **Document Preview** - View extracted text and document statistics
- 💾 **Chat History** - Maintains conversation context for better answers
- ⚡ **Fast Processing** - Optimized for quick responses

## 🎯 Demo

<!-- Add your demo GIF here -->
<!-- ![Demo](demo/app-demo.gif) -->

**How it works:**
1. Upload a PDF document
2. Click "Process PDFs" to extract text
3. Ask questions in natural language
4. Get AI-powered answers instantly

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **PDF Processing:** PyPDF2
- **AI Model:** Ollama (llama3, gemma3)
- **Language:** Python 3.8+
- **HTTP Requests:** requests library

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.8 or higher
- pip (Python package manager)
- Ollama

## 🚀 Installation

### Step 1: Install Ollama

**macOS:**
```bash
# Download and install from https://ollama.ai/download
# Or use Homebrew
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Windows:**
Download from https://ollama.ai/download

### Step 2: Download AI Models

```bash
# Download llama3 (8B parameters - better quality)
ollama pull llama3

# Download gemma3 (1B parameters - faster)
ollama pull gemma3:1b
```

### Step 3: Clone the Repository

```bash
git clone https://github.com/yourusername/pdf-reader.git
cd pdf-reader
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 5: Install Dependencies

```bash
pip install -r requirements.txt
```

## 🎮 Usage

### Step 1: Start Ollama Server

Open a terminal and run:

```bash
ollama serve
```

Keep this terminal running in the background.

### Step 2: Run the Application

In a new terminal:

```bash
# Navigate to project directory
cd pdf-reader

# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app.py
```

### Step 3: Access the Application

Open your browser and go to:
```
http://localhost:8501
```

### Step 4: Use the App

1. **Select Model:** Choose between llama3 or gemma3 in the sidebar
2. **Upload PDF:** Click "Choose PDF files" and select your document(s)
3. **Process:** Click "🔄 Process" to extract text
4. **Ask Questions:** Type your question in the chat input
5. **Get Answers:** Wait for the AI to analyze and respond

## 📖 Example Questions

Try asking questions like:

- "What is this document about?"
- "Summarize the key points"
- "What does it say about [specific topic]?"
- "List the main conclusions"
- "Explain [concept] mentioned in the document"
- "Compare the information in both documents"

## 🏗️ Project Structure

```
pdf-reader/
├── app.py                 # Main Streamlit application
├── main.py                # Core utilities and helper functions
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── htmlTemplates.py      # Legacy HTML templates
├── tool_registry.py      # Legacy tool registry
├── pdf_reader.ipynb      # Jupyter notebook prototype
└── venv/                 # Virtual environment (create this)
```

## 🔧 Configuration

### Changing AI Model Settings

Edit `app.py` to modify AI behavior:

```python
# Line ~70 - Adjust response length
"num_predict": 300,  # Increase for lon
