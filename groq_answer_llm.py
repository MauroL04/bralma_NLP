from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

if not groq_key:
    print("GROQ API key is missing!")
else:
    print("GROQ key found!")

def ask_question(question):
    if not groq_key:
        return "GROQ API key is missing!"
    client = Groq(api_key=groq_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": f"Answer in the spoken language:\n{question}"}],
        model="llama-3.3-70b-versatile",
    )
    return chat_completion.choices[0].message.content

def answer_with_context(question, context=""):
    if not groq_key:
        return "GROQ API key is missing!"
    client = Groq(api_key=groq_key)
    if context:
        prompt = (
            "Answer in the spoken language. \n\n"
            f"Context:\n{context}\n\n"
            f"User question:\n{question}\n\n"
            "Use the context if it is relevnt to the user question!!"
            "Make lists or bullet points clear, each with their own line."
        )
    else:
        prompt = (
            f"Answer in the spoken language:\n{question}\n\n"
        )
    answer_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    answer = answer_completion.choices[0].message.content
    return answer

def answer_and_maybe_quiz(question, context=""):
    answer = answer_with_context(question, context)
    quiz = ""
    if context:
        from groq_quiz_llm import generate_quiz
        quiz = generate_quiz(answer)
    if quiz:
        return f"{answer}\n{quiz}"
    else:
        return answer
