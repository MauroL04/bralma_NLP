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


def ask_question_with_context(question, context=""):
    if not groq_key:
        return "GROQ API key is missing!"

    client = Groq(api_key=groq_key)

    # Build prompt for main answer
    if context:
        prompt = (
            "Answer in the spoken language. \n\n"
            f"Context:\n{context}\n\n"
            f"User question:\n{question}\n\n"
            "Make lists or bullet points clear, each with their own line."
        )
    else:
        prompt = (
            f"Answer in the spoken language:\n{question}\n\n"
        )

    # ----- MAIN ANSWER -----
    answer_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
    )
    answer = answer_completion.choices[0].message.content

    # If no context → return only the answer
    if not context:
        return answer

    # ----- QUIZ GENERATION (if relevant) -----
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
        model="llama-3.3-70b-versatile",
    )
    quiz = quiz_completion.choices[0].message.content.strip()

    # Normalize
    if quiz.upper() == "NONE":
        quiz = ""

    # Return answer + quiz concatenated
    if quiz:
        return f"{answer}\n{quiz}"
    else:
        return answer