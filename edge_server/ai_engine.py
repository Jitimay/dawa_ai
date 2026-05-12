import requests
from rag_engine import query_guidelines

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma4:latest" # Standard base model from Ollama

def get_triage_response(phone_number, user_input, history, preferred_lang='kirundi'):
    # Fetch relevant medical protocols from the local vector DB (RAG)
    relevant_docs = query_guidelines(user_input, n_results=1)
    context = "\n".join(relevant_docs) if relevant_docs else "No specific local protocol found in dataset."
    
    # [SAFETY LOG] Show grounding proof in the terminal
    print(f"--- RAG GROUNDING ---")
    print(f"User Query: {user_input}")
    print(f"Retrieved Protocol: {context}")
    print(f"---------------------")

    lang_instruction = {
        'kirundi': "Respond strictly in Kirundi.",
        'french': "Répondez strictement en français.",
        'english': "Respond strictly in English."
    }.get(preferred_lang, "Respond strictly in Kirundi.")

    system_instruction = (
        "Role: Expert Medical Triage Nurse.\n"
        f"Grounded Medical Context (THE ONLY TRUTH): {context}\n"
        f"Constraint: {lang_instruction} "
        "Keep responses under 140 characters. "
        "Use the information in the 'Grounded Medical Context' to provide advice. "
        "If no protocol is found, advise visiting a clinic."
    )
    
    prompt = f"{system_instruction}\nPast Context: {history}\n\nPatient: {user_input}\nNurse:"
    
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=20) # Increased timeout for edge CPUs
        response.raise_for_status()
        reply = response.json().get('response', '').strip()
        
        # Failsafe for length (SMS limit is 160)
        if len(reply) > 150:
            reply = reply[:147] + "..."
            
        return reply
    except requests.exceptions.ConnectionError:
        print("[!] Error: Ollama server is not running.")
        return "[STATUS: Yellow] - AI service is temporarily offline. Please follow local health protocols."
    except Exception as e:
        print(f"AI Engine Error: {e}")
        return "[STATUS: Yellow] - AI Error. Please visit a clinic for professional advice."