from datetime import datetime
import json
import os
import re
from uuid import uuid4
import gradio as gr
import requests
from quiz_handler import get_quiz, check_answer

# Constants
MAX_TURNS = 15
CONTEXT_TURNS = 4
SAVE_DIR = "saved_chats"
MEMORY_FILE = "persistent_memory.json"
CHORD_FILE = "guitar_chord_dictionary_with_diagrams.json"
os.makedirs(SAVE_DIR, exist_ok=True)

model_options = {
    "LLaMA 3 (General / Python)": "llama3",
    "Mistral (Guitar / Music Theory)": "mistral",
    "⚠️ DeepSeek Coder v2 (Heavy - Code Focused)": "deepseek-coder-v2"
}

def get_system_prompt(model_name):
    if model_name == "mistral":
        return "You are a guitar tutor. Only respond to music topics. Use local diagrams only, no external links or tools."
    elif model_name == "deepseek-coder-v2":
        return "You are an advanced coding assistant. Help with algorithms and explain code clearly."
    return "You are a Python tutor. Teach concepts clearly. Quiz the user only when they ask."

# Load chord data
if os.path.exists(CHORD_FILE):
    with open(CHORD_FILE, "r") as f:
        chord_data = json.load(f)
else:
    chord_data = []

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"student_name": "Brandon", "knowledge_level": "intermediate", "last_sessions": []}

def update_memory(new_topic, model, summary, next_up, score=None, difficulty=None):
    memory = load_memory()
    memory["last_sessions"].append({
        "topic": new_topic,
        "model": model,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": summary,
        "recommended_next": next_up,
        "score": score or "n/a",
        "difficulty": difficulty or "intermediate"
    })
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def get_session_path(name):
    return os.path.join(SAVE_DIR, f"{name}.json")

def save_session(name, log):
    with open(get_session_path(name), "w") as f:
        json.dump(log, f, indent=2)

def load_session(name):
    path = get_session_path(name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def list_sessions():
    return [f[:-5] for f in os.listdir(SAVE_DIR) if f.endswith(".json")]

def generate_session_name():
    return f"session_{datetime.now().strftime('%Y-%m-%d_%H-%M')}_{uuid4().hex[:4]}"

def format_message(role, content):
    timestamp = datetime.now().strftime("%H:%M")
    speaker = "🧠 Tutor" if role == "assistant" else "🧍 You"
    return {"role": role, "content": f"**{speaker} ({timestamp})**\n\n{content}"}

def stream_model(model_name, history):
    messages = [{"role": "system", "content": get_system_prompt(model_name)}] + history[-CONTEXT_TURNS:]
    try:
        with requests.post("http://localhost:11434/api/chat",
                           json={"model": model_name, "messages": messages, "stream": True},
                           stream=True, timeout=60) as resp:
            buffer = ""
            for line in resp.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode("utf-8"))
                        token = data.get("message", {}).get("content", "")
                        buffer += token
                        yield buffer
                    except Exception:
                        continue
    except Exception as e:
        yield f"❌ Error: {str(e)}"

# Quiz State Memory
def ensure_quiz_memory(mem, user_id="Brandon"):
    if "quiz_memory" not in mem:
        mem["quiz_memory"] = {}
    if user_id not in mem["quiz_memory"]:
        mem["quiz_memory"][user_id] = {
            "topic_counts": {},
            "current_quiz": None,
            "correct": 0,
            "wrong": 0,
            "streak": 0,
            "difficulty": "intermediate",
            "attempt_log": [],
            "quiz_ready": False
        }

def quiz_mode_from_difficulty(difficulty):
    return "multiple_choice" if difficulty == "easy" else "typing"

def generate_adaptive_quiz(mem, subject, user_id="Brandon"):
    ensure_quiz_memory(mem, user_id)
    difficulty = mem["quiz_memory"][user_id]["difficulty"]
    mode = quiz_mode_from_difficulty(difficulty)
    quiz = get_quiz(subject, mode)
    mem["quiz_memory"][user_id]["current_quiz"] = quiz
    question = f"🧠 Let's quiz! ({difficulty.title()})\n\n{quiz['question']}"
    if 'choices' in quiz:
        question += f"\n\n**Choices:** {', '.join(quiz['choices'])}"
    return question

def process_quiz_response(mem, user_input, user_id="Brandon"):
    quiz_state = mem["quiz_memory"][user_id]
    quiz = quiz_state.get("current_quiz")
    if not quiz:
        return None, "❌ No quiz in progress."

    correct = check_answer(user_input, quiz["answer"])
    quiz_state["attempt_log"].append({
        "question": quiz["question"],
        "your_answer": user_input,
        "correct_answer": quiz["answer"],
        "correct": correct
    })
    quiz_state["current_quiz"] = None
    quiz_state["quiz_ready"] = False

    if correct:
        quiz_state["correct"] += 1
        quiz_state["streak"] += 1
        feedback = "✅ Correct!"
    else:
        quiz_state["wrong"] += 1
        quiz_state["streak"] = 0
        feedback = f"❌ Incorrect. The correct answer was: {quiz['answer']}"

    if quiz_state["correct"] >= 10:
        quiz_state["difficulty"] = "hard"
    elif quiz_state["correct"] >= 5:
        quiz_state["difficulty"] = "medium"
    elif quiz_state["wrong"] >= 3:
        quiz_state["difficulty"] = "easy"

    return correct, feedback

def chat_stream(message, history, model_label, session_name, difficulty_choice):
    model_name = model_options[model_label]
    history = history or []
    if not session_name:
        session_name = generate_session_name()

    prompt = message if isinstance(message, str) else message["content"]
    memory = load_memory()
    ensure_quiz_memory(memory, "Brandon")
    memory["quiz_memory"]["Brandon"]["difficulty"] = difficulty_choice

    if any(k in prompt.lower() for k in ["quiz me", "test me", "challenge me"]):
        memory["quiz_memory"]["Brandon"]["quiz_ready"] = True

    if memory["quiz_memory"]["Brandon"].get("current_quiz"):
        correct, feedback = process_quiz_response(memory, prompt)
        save_session(session_name, history + [format_message("user", prompt), format_message("assistant", feedback)])
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
        return history + [format_message("user", prompt), format_message("assistant", feedback)], "", session_name, history + [format_message("user", prompt), format_message("assistant", feedback)], ""

    if memory["quiz_memory"]["Brandon"]["quiz_ready"]:
        try:
            quiz_text = generate_adaptive_quiz(memory, "python")
        except Exception as e:
            quiz_text = f"❌ Failed to generate quiz: {str(e)}"
        with open(MEMORY_FILE, "w") as f:
            json.dump(memory, f, indent=2)
        return history + [format_message("user", prompt), format_message("assistant", quiz_text)], "", session_name, history + [format_message("user", prompt), format_message("assistant", quiz_text)], ""

    new_history = history + [{"role": "user", "content": prompt}]
    response_buffer = ""
    for partial in stream_model(model_name, new_history):
        response_buffer = partial
        yield new_history + [format_message("assistant", response_buffer)], "", session_name, new_history, ""

    final_history = new_history + [{"role": "assistant", "content": response_buffer}]
    save_session(session_name, final_history)

    # Visual chord rendering fix
    if model_name == "mistral":
        response_buffer = re.sub(r"!\[.*?\]\(.*?\)", "", response_buffer)
        if any(k in prompt.lower() for k in ["chord", "scale", "major", "open", "diagram"]):
            # Instead of looking for entry["content"], build visuals from chord dictionary
            visuals = []
            for name, data in chord_data.items():
                if any(t in name.lower() for t in ["major", "chord", "open", "scale"]):
                    visuals.append(f"**{name}**\n![{name}]({data['diagram']})")
            visual_output = "\n\n".join(visuals[:5]) if visuals else "🎸 No diagrams available."
            yield final_history + [format_message("assistant", response_buffer)], "", session_name, final_history, visual_output


# Gradio UI
def summarize_memory():
    mem = load_memory()
    logs = mem["last_sessions"][-5:]
    return "\n".join([f"[{s['datetime']}] {s['topic']} ({s['model']}): {s['summary'][:50]}..." for s in logs])

with gr.Blocks(css="footer {display:none !important}") as demo:
    with gr.Row():
        with gr.Column(scale=1):
            saved_sessions = gr.Dropdown(choices=list_sessions(), label="Load Session", interactive=True)
            load_btn = gr.Button("📂 Load")
            session_name = gr.Textbox(label="💾 Session Name", placeholder="Auto-generated if blank")
            new_btn = gr.Button("🧹 New Chat")
            difficulty = gr.Radio(["easy", "intermediate", "hard"], value="intermediate", label="📈 Start Difficulty")
            analytics = gr.Textbox(label="📊 Recent Sessions", lines=8, interactive=False)
        with gr.Column(scale=3):
            gr.Markdown("### 🎓 AI Tutor Chatbot (Stable Version)")
            chat_window = gr.Chatbot(label="Chat", height=500, type="messages")
            model_picker = gr.Radio(choices=list(model_options.keys()), value="LLaMA 3 (General / Python)", label="Model")
            status = gr.Markdown()
            chatbot_input = gr.Textbox(placeholder="Type your question and press Enter", show_label=False)

    chat_state = gr.State([])
    current_session_name = gr.State("")

    chatbot_input.submit(
        fn=chat_stream,
        inputs=[chatbot_input, chat_state, model_picker, session_name, difficulty],
        outputs=[chat_window, status, current_session_name, chat_state, chatbot_input],
        show_progress=True
    )
    def clear_all():
        return [], "", generate_session_name(), [], ""

    new_btn.click(fn=clear_all, outputs=[chat_window, status, current_session_name, chat_state, chatbot_input])
    load_btn.click(fn=lambda name: (load_session(name), "", name, load_session(name), ""), inputs=[saved_sessions],
                   outputs=[chat_window, status, current_session_name, chat_state, chatbot_input])
    load_btn.click(fn=summarize_memory, inputs=[], outputs=analytics)

demo.launch()
