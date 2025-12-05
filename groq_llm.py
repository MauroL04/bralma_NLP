from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()  # leest automatisch .env uit

groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    print("GROQ API key ontbreekt!")
else:
    print("GROQ key gevonden!")

def ask_question(question):
    if not groq_key:
        return "GROQ API key ontbreekt!"
    client = Groq(api_key=groq_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": question}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content


def ask_question_with_context(question, context=""):
    if not groq_key:
        return "GROQ API key ontbreekt!"
    prompt = question
    if context:
        prompt = f"Context:\n{context}\n\nVraag:\n{question}"
    client = Groq(api_key=groq_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content