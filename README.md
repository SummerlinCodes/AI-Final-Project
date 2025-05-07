# AI-Powered Chatbot for Personalized Learning

## Project Overview

This chatbot provides adaptive tutoring support in both **Python programming** and **Guitar music theory**. Built with the **Ollama framework**, it uses **locally hosted LLMs** for fast, private, and customizable interactions.

The system dynamically adapts explanations, quizzes the user, and provides inline guitar chord diagrams using `matplotlib`.

---

## Features

- Adaptive tutoring with model-specific routing
- Real-time quiz generation with memory tracking
- Guitar chord diagram generation with `matplotlib`
- Local persistent memory and session management
- Multi-turn chat via Gradio interface with streaming
- Offline, fast inference using:
  - **LLaMA 3** for Python/general help
  - **DeepSeek Coder v2** for intensive coding queries
  - **Mistral** for music/guitar tutoring

---

## Requirements

- Python 3.9+
- [Ollama](https://ollama.com) installed and running (used for local models)
- Python libraries:
  - `gradio`
  - `matplotlib`
  - `uuid`
  - `requests`

You can install dependencies with:

```bash
pip install -r requirements.txt
```

---

## How to Run

1. **Create and activate a virtual environment (recommended)**

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
.venv\Scripts\activate

# Activate on macOS/Linux
source venv/bin/activate
```

2. **Install required Python packages**

```bash
pip install -r requirements.txt
```

3. **Start Ollama in the background**
(Make sure you've pulled the necessary models)

```bash
ollama pull llama3
ollama pull deepseek-coderv2
ollama pull mistral
```

4. **Run the chatbot UI**

```bash
python chatbot.py
```

5. **(Optional)** To regenerate guitar chord diagrams:

```bash
python generate_chord_diagrams.py
```


## Project Structure

```
├── chatbot.py       # Main chatbot logic + Gradio UI
├── generate_chord_diagrams.py         # Creates PNG diagrams from chord data
├── persistent_memory.json             # Memory for quiz tracking
├── guitar_chord_dictionary_with_diagrams.json
├── saved_chats/                       # Past chat session logs
├── diagrams/                          # Auto-generated chord diagrams
└── requirements.txt                   # Python dependencies
```

---

## Notes

- This project is 100% local and everything is run via Ollama model wise.
- You can customize your model routing logic in the Python file to support more subjects or switch behavior.
- For best performance, run on a system with ≥12GB RAM

---

Enjoy your personalized, multi-use AI tutor!
