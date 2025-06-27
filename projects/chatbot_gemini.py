import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GOOGLE_API_KEY)
model = genai.GenerativeModel("models/gemini-1.5-flash")

def ask_gemini(user_prompt):
    try:
        # Simple greetings — short friendly reply
        simple_greetings = ["hi", "hello", "hey", "good morning", "good evening", "good afternoon"]
        if user_prompt.strip().lower() in simple_greetings:
            return "Hi there! I'm here to help you understand this project. Ask me anything about it!"

        # Else, build full prompt
        system_instruction = (
            "You are a helpful AI assistant for a student project showcase platform called VidyaVault. "
            "Do not suggest modifying the project. "
        )

        full_prompt = f"{system_instruction}\n\nUser question: {user_prompt}"
        response = model.generate_content(full_prompt)
        return response.text

    except Exception as e:
        return f"Error: {str(e)}"
