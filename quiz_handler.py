
import random

# Sample quiz data
quizzes = {
    "python": {
        "multiple_choice": [
            {
                "question": "What does a 'for' loop do?",
                "choices": ["Executes code once", "Repeats code while a condition is true", "Repeats code for each item in a list", "Defines a function"],
                "answer": "Repeats code for each item in a list"
            },
            {
                "question": "Which keyword is used to define a function in Python?",
                "choices": ["func", "define", "def", "function"],
                "answer": "def"
            }
        ],
        "typing": [
            {
                "question": "Type the syntax to create a list with the numbers 1 to 5.",
                "answer": "[1, 2, 3, 4, 5]"
            },
            {
                "question": "Type the keyword used to end a function in Python.",
                "answer": "return"
            }
        ]
    },
    "music": {
        "multiple_choice": [
            {
                "question": "Which of these is a major chord?",
                "choices": ["Am", "G", "Em", "Dm"],
                "answer": "G"
            },
            {
                "question": "Which string is the thickest on a standard guitar?",
                "choices": ["1st (high E)", "3rd (G)", "5th (A)", "6th (low E)"],
                "answer": "6th (low E)"
            }
        ],
        "typing": [
            {
                "question": "Type the chord name that uses the fingering '022000'.",
                "answer": "E minor"
            },
            {
                "question": "Type the note that follows G in the A major scale.",
                "answer": "A"
            }
        ]
    }
}

def get_quiz(subject="python", mode="multiple_choice"):
    items = quizzes.get(subject, {}).get(mode, [])
    return random.choice(items) if items else None

def check_answer(user_answer, correct_answer):
    return user_answer.strip().lower() == correct_answer.strip().lower()

# Example usage:
if __name__ == "__main__":
    q = get_quiz("python", "typing")
    print("Q:", q["question"])
    print("A:", q["answer"])
