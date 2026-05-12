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
    "indwara", "urgence", "emergency",
    "cancer", "kanseri", "ububabare bukabije", "severe pain"
]

LOG_FILE = "triage_logs.csv"

def find_arduino_port():
    """Dynamically finds the serial port for Arduino Nano RP2040 GSM gateway."""
    ports = serial.tools.list_ports.comports()
    for port in ports:
        # Common Arduino/Serial adapter identifiers
        if "Arduino" in port.description or "RP2040" in port.description or "ttyACM" in port.device:
            return port.device
    return None

def connect_to_gateway():
    """Attempts to establish serial connection with the gateway."""
    port = find_arduino_port()
    if not port:
        print("[!] Searching for Gateway... (Ensure Arduino is plugged in)")
        return None
        
    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2) # Wait for Arduino reset
        ser.reset_input_buffer()
        print(f"[✓] Connected to Gateway on {port}")
        return ser
    except Exception as e:
        print(f"[X] Connection Error: {e}")
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
    print("\n" + "="*42)
    print("   DAWA_AI: OFFLINE AI HEALTH GATEWAY   ")
    print("="*42 + "\n")
    
    # 1. Initialize the local database
    init_db()
    print("[1/3] Local Database Initialized.")

    ser = None
    print("[2/3] Establishing Gateway Link...")
    
    # 2. Reconnection Loop
    while True:
        try:
            if ser is None or not ser.is_open:
                ser = connect_to_gateway()
                if ser is None:
                    time.sleep(5)
                    continue
                print("[3/3] System Online. Waiting for incoming SMS...")
                print("-" * 42)

            if ser.in_waiting > 0:
                line = ser.readline().decode('utf-8', errors='ignore').strip()
                
                if line.startswith("MSG|"):
                    parts = line.split('|', 2)
                    
                    if len(parts) == 3:
                        phone_number = parts[1].strip()
                        user_text = parts[2].strip()
                        
                        print(f"\n[INBOUND] {phone_number}: {user_text}")

                        # --- REGISTRATION ---
                        if user_text.startswith("REG|"):
                            reg_parts = user_text.split('|')
                            if len(reg_parts) == 2 and reg_parts[1] == REG_PASSWORD:
                                register_user(phone_number)
                                msg = "[SYSTEM] Murakoze! Inomero yanyu yaremewe. (Number verified.)"
                                ser.write(f"SEND|{phone_number}|{msg}\n".encode('utf-8'))
                                log_interaction(phone_number, user_text, msg, "REGISTRATION")
                                continue

                        # --- LANGUAGE SELECTION ---
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

                        # --- SECURITY CHECK ---
                        if not is_verified(phone_number):
                            print(f"[!] Blocked unverified number: {phone_number}")
                            denial_msg = "[SYSTEM] Inomero yanyu ntiyaremewe. Vugana n'umukozi w'amagara. (Number not verified.)"
                            ser.write(f"SEND|{phone_number}|{denial_msg}\n".encode('utf-8'))
                            log_interaction(phone_number, user_text, denial_msg, "UNVERIFIED")
                            continue

                        # --- RED FLAG DETECTION ---
                        if detect_red_flag(user_text):
                            emergency_msg = "[STATUS: RED] - URGENT: Genda kwa muganga ubu nyene! (Emergency: Go to the hospital immediately!)"
                            print("!!! EMERGENCY DETECTED: RED FLAG TRIGGERED !!!")
                            ser.write(f"SEND|{phone_number}|{emergency_msg}\n".encode('utf-8'))
                            log_interaction(phone_number, user_text, emergency_msg, "EMERGENCY")
                            continue

                        # --- SESSION RESET ---
                        if user_text.upper() in RESET_KEYWORDS:
                            new_id = create_new_thread(phone_number)
                            confirm_msg = "[SYSTEM] Intango nshasha yatanguye. Tugufashe gute? (New session started.)"
                            ser.write(f"SEND|{phone_number}|{confirm_msg}\n".encode('utf-8'))
                            log_interaction(phone_number, user_text, confirm_msg, "RESET")
                            continue

                        # --- AI CONSULTATION ---
                        thread_id = get_active_thread(phone_number)
                        add_message(thread_id, 'user', user_text)
                        history = get_thread_history(thread_id)
                        user_lang = get_user_lang(phone_number)

                        print(f"[AI] Consulting Gemma 4 (ID: {thread_id})...")
                        ai_reply = get_triage_response(phone_number, user_text, history, user_lang)
                        
                        add_message(thread_id, 'assistant', ai_reply)
                        ser.write(f"SEND|{phone_number}|{ai_reply}\n".encode('utf-8'))
                        print(f"[OUTBOUND] Sent to {phone_number}: {ai_reply}")
                        log_interaction(phone_number, user_text, ai_reply, "AI_RESPONSE")
            
            time.sleep(0.1) # Prevent CPU hogging

        except serial.SerialException:
            print("[X] Gateway Lost Connection. Attempting to reconnect...")
            if ser:
                ser.close()
            ser = None
            time.sleep(2)
        except KeyboardInterrupt:
            print("\n[!] Shutting down Dawa AI Server...")
            if ser:
                ser.close()
            break
        except Exception as e:
            print(f"[CRITICAL ERROR] {e}")
            time.sleep(2)

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()