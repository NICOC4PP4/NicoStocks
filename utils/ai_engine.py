import os
import json
import google.generativeai as genai
from typing import List, Dict

# Configurar Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def analyze_news_impact(news_texts: List[str]) -> Dict:
    """
    Analiza una lista de textos de noticias y devuelve JSON estructurado usando Google Gemini.
    """
    if not GEMINI_API_KEY:
         return {"summary": "No Gemini API Key found", "sentiment": 0, "impact_level": "low"}

    combined_text = "\n".join(news_texts[:5]) 
    
    prompt = f"""
    Eres un analista financiero experto. Analiza las siguientes noticias:
    {combined_text}
    
    Responde ÚNICAMENTE con un JSON válido siguiendo estrictamente este esquema:
    {{
        "summary": "Resumen ejecutivo de 1 frase en español",
        "sentiment": float (entre -1.0 muy negativo y 1.0 muy positivo),
        "impact_level": "high" | "med" | "low"
    }}
    """
    
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        # Forzar respuesta JSON
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        return json.loads(response.text)
    except Exception as e:
        print(f"Gemini AI Error: {e}")
        return {"summary": "Error analyzing", "sentiment": 0, "impact_level": "low"}
