import serial
import serial.tools.list_ports
import time
import sys
import csv
import os
from datetime import datetime
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

# --- CONFIGURATION ---
BAUD_RATE = 115200     # Match this with your Arduino's Serial.begin()

# Keywords that will trigger a fresh conversation thread for the user
RESET_KEYWORDS = ["NEW", "GISHASHA", "RESET", "OKUVA"]
# Admin password for remote registration via SMS (Example: REG|PASSWORD)
REG_PASSWORD = "MAJIDAWA_2026"

# Emergency "Red Flag" Keywords (Kirundi, French, English)
RED_FLAG_KEYWORDS = [
    "amaraso", "ukuvira", "hemorragie", "bleeding",
    "umuriro mwinshi", "fievre elevee", "high fever",
    "gutitira", "crise", "convulsion",
    "kuzitirwa", "inconscient", "unconscious",
    "guhumeka nabi", "difficulte respiratoire", "breathing",
    "indwara", "urgence", "emergency"
]

LOG_FILE = "triage_logs.csv"

def find_arduino_port():
    """Dynamically finds the serial port for Arduino/GSM gateway."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Common Arduino/Serial adapter identifiers
        if "Arduino" in port.description or "USB Serial" in port.description or "ttyACM" in port.device or "ttyUSB" in port.device:
            return port.device
    return None

def detect_red_flag(text):
    """Checks if the message contains any emergency keywords."""
    text_lower = text.lower()
    for keyword in RED_FLAG_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def log_interaction(phone, message, response, triage_status):
    """Logs the interaction to a CSV file for technical writeup data."""
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Timestamp", "Phone", "Message", "Response", "Status"])
        writer.writerow([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), phone, message, response, triage_status])

def main():
    print("==========================================")
    print("   DAWA_AI: OFFLINE AI HEALTH GATEWAY   ")
    print("==========================================")
    
    # 1. Initialize the local database
    init_db()
    print("[1/3] Local Database Initialized.")

    # 2. Establish Serial Connection with Arduino
    port = find_arduino_port()
    if not port:
        print("[ERROR] Could not find Arduino. Please check connection.")
        sys.exit(1)
        
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2) 
        ser.reset_input_buffer()
        print(f"[2/3] Connected to Gateway on {port}")
    except Exception as e:
        print(f"[ERROR] Could not connect to {port}: {e}")
        sys.exit(1)

    print("[3/3] System Online. Waiting for incoming SMS...")
    print("------------------------------------------")

    while True:
        try:
            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.startswith("MSG|"):
                    parts = line.split('|', 2)
                    
                    if len(parts) == 3:
                        phone_number = parts[1].strip()
                        user_text = parts[2].strip()
                        
                        print(f"\n[RECEIVED] From: {phone_number}")
                        print(f"Message: {user_text}")

                        # --- STEP 0: REGISTRATION LOGIC ---
                        if user_text.startswith("REG|"):
                            reg_parts = user_text.split('|')
                            if len(reg_parts) == 2 and reg_parts[1] == REG_PASSWORD:
                                register_user(phone_number)
                                msg = "[SYSTEM] Murakoze! Inomero yanyu yaremewe. (Number verified.)"
                                ser.write(f"SEND|{phone_number}|{msg}\n".encode('utf-8'))
                                log_interaction(phone_number, user_text, msg, "REGISTRATION")
                                continue

                        # --- STEP 0.1: LANGUAGE SELECTION ---
                        if user_text.startswith("LANG|"):
                            lang_parts = user_text.split('|')
                            if len(lang_parts) == 2:
                                requested_lang = lang_parts[1].lower()
                                if requested_lang in ['kirundi', 'french', 'english']:
                                    set_user_lang(phone_number, requested_lang)
                                    confirm_msg = f"[SYSTEM] Ururimi rwahinduwe kuri {requested_lang}. (Language set to {requested_lang}.)"
                                    ser.write(f"SEND|{phone_number}|{confirm_msg}\n".encode('utf-8'))
                                    log_interaction(phone_number, user_text, confirm_msg, "LANG_CHANGE")
                                    continue

                        # --- STEP 1: SECURITY CHECK ---
                        if not is_verified(phone_number):
                            print(f"Rejected: {phone_number} is not verified.")
                            denial_msg = "[SYSTEM] Inomero yanyu ntiyaremewe. Vugana n'umukozi w'amagara. (Number not verified. Contact health worker.)"
                            ser.write(f"SEND|{phone_number}|{denial_msg}\n".encode('utf-8'))
                            log_interaction(phone_number, user_text, denial_msg, "UNVERIFIED")
                            continue

                        # --- STEP 2: RED FLAG DETECTION (SAFETY FIRST) ---
                        if detect_red_flag(user_text):
                            emergency_msg = "[STATUS: RED] - URGENT: Genda kwa muganga ubu nyene! (Emergency: Go to the hospital immediately!)"
                            print("!!! RED FLAG DETECTED !!!")
                            ser.write(f"SEND|{phone_number}|{emergency_msg}\n".encode('utf-8'))
                            log_interaction(phone_number, user_text, emergency_msg, "EMERGENCY")
                            continue

                        # --- STEP A: CHECK FOR RESET KEYWORDS ---
                        if user_text.upper() in RESET_KEYWORDS:
                            new_id = create_new_thread(phone_number)
                            confirm_msg = "[SYSTEM] Intango nshasha yatanguye. Tugufashe gute? (New session started.)"
                            ser.write(f"SEND|{phone_number}|{confirm_msg}\n".encode('utf-8'))
                            log_interaction(phone_number, user_text, confirm_msg, "RESET")
                            continue

                        # --- STEP B: MANAGE SESSION & HISTORY ---
                        thread_id = get_active_thread(phone_number)
                        add_message(thread_id, 'user', user_text)
                        history = get_thread_history(thread_id)
                        user_lang = get_user_lang(phone_number)

                        # --- STEP C: INVOKE GEMMA 4 (RAG ENABLED) ---
                        print(f"Consulting Gemma 4 (Thread ID: {thread_id}, Lang: {user_lang})...")
                        ai_reply = get_triage_response(phone_number, user_text, history, user_lang)
                        
                        # --- STEP D: SAVE & DISPATCH ---
                        add_message(thread_id, 'assistant', ai_reply)
                        ser.write(f"SEND|{phone_number}|{ai_reply}\n".encode('utf-8'))
                        print(f"Action: Dispatched AI reply.")
                        log_interaction(phone_number, user_text, ai_reply, "AI_RESPONSE")

        except KeyboardInterrupt:
            print("\nShutting down MajiDawa Server...")
            ser.close()
            break
        except Exception as e:
            print(f"[CRITICAL ERROR] Loop crashed: {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()