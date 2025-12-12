from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

def generate_quiz(answer):
    if not groq_key:
        return ""
    client = Groq(api_key=groq_key)
    quiz_prompt = (
        "Based on the user's question and the provided context, decide whether a quiz"
        "would be relevant.\n\n"
        "If relevant: generate 5 short quiz questions in the spoken language. No answers. List them from 1 to 5.\n"
        "Make sure that a quiz actually helps the user to understand to topic better. Do quizes when you talk about information"
        "DO not say that the user asked for a quiz, just provide it at the end. Give the quize the title ## Quiz"
        "If not relevant: return ONLY the word: NONE"
    )
    quiz_completion = client.chat.completions.create(
        messages=[
            {"role": "assistant", "content": answer},
            {"role": "user", "content": quiz_prompt},
        ],
        model="openai/gpt-oss-20b",
    )
    quiz = quiz_completion.choices[0].message.content.strip()
    if quiz.upper() == "NONE":
        return ""
    return quiz
