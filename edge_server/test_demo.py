import time
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager import (
    init_db, 
    get_active_thread, 
    create_new_thread, 
    add_message, 
    get_thread_history,
    is_verified,
    register_user,
    get_user_lang,
    set_user_lang
)
from ai_engine import get_triage_response

# --- CONFIGURATION (Synced with main.py) ---
REG_PASSWORD = "MAJIDAWA_2026"
RESET_KEYWORDS = ["NEW", "GISHASHA", "RESET", "OKUVA"]
RED_FLAG_KEYWORDS = [
    "amaraso", "ukuvira", "hemorragie", "bleeding",
    "umuriro mwinshi", "fievre elevee", "high fever",
    "gutitira", "crise", "convulsion",
    "kuzitirwa", "inconscient", "unconscious",
    "guhumeka nabi", "difficulte respiratoire", "breathing",
    "indwara", "urgence", "emergency",
    "cancer", "kanseri", "ububabare bukabije", "severe pain"
]

def detect_red_flag(text):
    text_lower = text.lower()
    for keyword in RED_FLAG_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def print_sms(sender, text, is_inbound=True):
    direction = "📩 INBOUND SMS" if is_inbound else "📤 OUTBOUND SMS"
    print("\n" + "-"*50)
    print(f"{direction}")
    print(f"From/To: {sender}")
    print(f"Content: {text}")
    print("-"*50)

def main():
    print("\n" + "="*60)
    print("   DAWA_AI: VIRTUAL HARDWARE EMULATOR (JUDGE MODE)   ")
    print("   Simulating GSM Gateway via CLI - No Hardware Required   ")
    print("="*60 + "\n")
    
    init_db()
    
    # Mock phone number for the demo
    DEMO_PHONE = "+257 1234 5678"
    
    print(f"[*] Simulating session for: {DEMO_PHONE}")
    print("[*] Tip: Start by sending 'REG|MAJIDAWA_2026' to verify your number.")
    print("[*] Tip: Change language with 'LANG|ENGLISH' or 'LANG|FRENCH'.")
    print("[*] Tip: Type 'EXIT' to stop the emulator.\n")

    while True:
        user_input = input(f"[{DEMO_PHONE}] > ").strip()
        
        if user_input.upper() == "EXIT":
            break
        
        if not user_input:
            continue

        print_sms(DEMO_PHONE, user_input, is_inbound=True)

        # --- REGISTRATION ---
        if user_input.startswith("REG|"):
            reg_parts = user_input.split('|')
            if len(reg_parts) == 2 and reg_parts[1] == REG_PASSWORD:
                register_user(DEMO_PHONE)
                msg = "[SYSTEM] Murakoze! Inomero yanyu yaremewe. (Number verified.)"
                print_sms(DEMO_PHONE, msg, is_inbound=False)
                continue
            else:
                msg = "[SYSTEM] Error: Invalid Password."
                print_sms(DEMO_PHONE, msg, is_inbound=False)
                continue

        # --- SECURITY CHECK ---
        if not is_verified(DEMO_PHONE):
            msg = "[SYSTEM] Inomero yanyu ntiyaremewe. Vugana n'umukozi w'amagara. (Number not verified.)"
            print_sms(DEMO_PHONE, msg, is_inbound=False)
            continue

        # --- LANGUAGE SELECTION ---
        if user_input.startswith("LANG|"):
            lang_parts = user_input.split('|')
            if len(lang_parts) == 2:
                requested_lang = lang_parts[1].lower()
                if requested_lang in ['kirundi', 'french', 'english']:
                    set_user_lang(DEMO_PHONE, requested_lang)
                    msg = f"[SYSTEM] Ururimi rwahinduwe kuri {requested_lang}. (Language set to {requested_lang}.)"
                    print_sms(DEMO_PHONE, msg, is_inbound=False)
                    continue

        # --- RED FLAG DETECTION ---
        if detect_red_flag(user_input):
            emergency_msg = "[STATUS: RED] - URGENT: Genda kwa muganga ubu nyene! (Emergency: Go to the hospital immediately!)"
            print_sms(DEMO_PHONE, emergency_msg, is_inbound=False)
            continue

        # --- SESSION RESET ---
        if user_input.upper() in RESET_KEYWORDS:
            create_new_thread(DEMO_PHONE)
            msg = "[SYSTEM] Intango nshasha yatanguye. Tugufashe gute? (New session started.)"
            print_sms(DEMO_PHONE, msg, is_inbound=False)
            continue

        # --- AI CONSULTATION ---
        thread_id = get_active_thread(DEMO_PHONE)
        add_message(thread_id, 'user', user_input)
        history = get_thread_history(thread_id)
        user_lang = get_user_lang(DEMO_PHONE)

        print(f"--- [EMULATOR LOG] Consulting Gemma 4 via Ollama... ---")
        ai_reply = get_triage_response(DEMO_PHONE, user_input, history, user_lang)
        
        add_message(thread_id, 'assistant', ai_reply)
        print_sms(DEMO_PHONE, ai_reply, is_inbound=False)

if __name__ == "__main__":
    main()
