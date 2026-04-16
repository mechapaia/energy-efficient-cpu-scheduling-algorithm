import google.generativeai as genai
import os

# Configure your Gemini API Key here
# It's recommended to set the GEMINI_API_KEY environment variable
GEMINI_API_KEY = "YOUR_API_KEY_HERE"

def get_ai_response(prompt: str) -> str:
    """
    Connects to Gemini API and returns a response for the given prompt.
    """
    key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY)
    
    if not key or key == "YOUR_API_KEY_HERE":
        return "Error: Gemini API Key not configured. Please set GEMINI_API_KEY in scheduler/ai.py or as an environment variable."

    try:
        genai.configure(api_key=key)
        model = genai.GenerativeModel(
            model_name='gemini-2.0-flash-lite',
            system_instruction=(
                "You are an expert AI assistant for a specialized Operating Systems project. "
                "The project is an MLFQ (Multi-Level Feedback Queue) CPU Scheduler simulation "
                "with DVFS (Dynamic Voltage and Frequency Scaling) energy-aware modeling. "
                "Context: The simulation uses 3-5 priority queues (Q0-Q4), tracks power using P=C*V^2*f, "
                "and monitors live system processes. Focus your answers on OS scheduling, "
                "energy efficiency, and the technical details of this specific implementation. "
                "CRITICAL: Since you are displayed in a narrow sidebar, prioritize brevity. "
                "Use bullet points for lists and short paragraphs. Avoid long blocks of text."
            )
        )
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"AI Error: {str(e)}"
