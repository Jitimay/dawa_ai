import requests
from rag_engine import query_guidelines

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma" 

def get_triage_response(phone_number, user_input, history, preferred_lang='kirundi'):
    # Fetch relevant medical protocols from the local vector DB (RAG)
    relevant_docs = query_guidelines(user_input, n_results=1)
    context = "\n".join(relevant_docs) if relevant_docs else "No specific local protocol found."

    lang_instruction = {
        'kirundi': "Respond primarily in Kirundi.",
        'french': "Répondez principalement en français.",
        'english': "Respond primarily in English."
    }.get(preferred_lang, "Respond primarily in Kirundi.")

    system_instruction = (
        "Role: You are an expert medical triage assistant for rural Burundi. "
        "Task: Assess symptoms and provide safe guidance based ONLY on the provided Context and Past Context. "
        "Rule 1: NEVER give a medical diagnosis. "
        f"Rule 2: {lang_instruction} "
        "Rule 3: Keep responses under 140 characters. "
        "Rule 4: If a Red Flag is detected, prioritize immediate hospital transfer.\n"
        f"Grounded Medical Context: {context}\n"
    )
    
    prompt = f"{system_instruction}\nPast Context: {history}\n\nPatient: {user_input}\nNurse:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        reply = response.json().get('response', '').strip()
        
        # Failsafe for length (SMS limit is 160)
        if len(reply) > 150:
            reply = reply[:147] + "..."
            
        return reply
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return "[STATUS: Yellow] - Error connecting to local AI. Please visit a clinic."