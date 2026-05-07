import requests
from rag_engine import query_guidelines

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "dawa-nurse" # Point to the fine-tuned model created via Modelfile

def get_triage_response(phone_number, user_input, history, preferred_lang='kirundi'):
    # Fetch relevant medical protocols from the local vector DB (RAG)
    relevant_docs = query_guidelines(user_input, n_results=1)
    context = "\n".join(relevant_docs) if relevant_docs else "No specific local protocol found."
    
    # [SAFETY LOG] Show grounding proof in the terminal
    print(f"--- RAG GROUNDING ---")
    print(f"User Query: {user_input}")
    print(f"Retrieved Protocol: {context}")
    print(f"---------------------")

    lang_instruction = {
        'kirundi': "Respond primarily in Kirundi.",
        'french': "Répondez principalement en français.",
        'english': "Respond primarily in English."
    }.get(preferred_lang, "Respond primarily in Kirundi.")

    system_instruction = (
        f"Grounded Medical Context (FACTS): {context}\n"
        f"Constraint: {lang_instruction} "
        "Keep responses under 140 characters."
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