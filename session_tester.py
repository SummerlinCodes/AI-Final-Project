
import json
import time
import requests

# Simulated conversation examples
conversations = [
    {
        "topic": "python",
        "model": "llama3",
        "messages": [
            "What is a for loop in Python?",
            "Can you give me an example with a list?",
            "What if I want to loop backwards?"
        ]
    },
    {
        "topic": "music",
        "model": "mistral",
        "messages": [
            "What are the easiest guitar chords to start with?",
            "Can you show me a diagram for C major?",
            "What's the difference between a major and minor chord?"
        ]
    }
]

def simulate_chat(model, messages):
    history = [{"role": "system", "content": "You are an adaptive AI tutor."}]
    for msg in messages:
        history.append({"role": "user", "content": msg})
        try:
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={"model": model, "messages": history[-4:], "stream": False},
                timeout=20
            )
            result = response.json()
            reply = result.get("message", {}).get("content", "[No reply]")
            print(f"🧍 You: {msg}")
            print(f"🧠 Bot: {reply[:150]}{'...' if len(reply) > 150 else ''}\n")
            history.append({"role": "assistant", "content": reply})
            time.sleep(1)
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    for convo in conversations:
        print(f"=== Simulating {convo['topic']} session with {convo['model']} ===\n")
        simulate_chat(convo["model"], convo["messages"])
        print("=" * 60 + "\n")
