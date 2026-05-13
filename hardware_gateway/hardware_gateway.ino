/**
 * DAWA AI: THE OFFLINE HEALTHCARE BRIDGE
 * Firmware for Arduino Nano RP2040 Connect + SIM800A
 * --------------------------------------------------
 * This firmware acts as a hardware bridge between the GSM network 
 * and the Edge Server (PC) running Gemma 4.
 * 
 * Hardware:
 * - Arduino Nano RP2040 Connect
 * - SIM800A GSM Module (connected to Serial1 / Pins 0 & 1)
 */

#include <Arduino.h>

// Configuration
#define GSM_BAUD 9600       // Standard stable baud for SIM800A
#define PC_BAUD 115200      // High speed for PC communication
#define gsm Serial1         // Hardware UART1 on RP2040

// Buffers and Flags
String gsmBuffer = "";
bool isReceivingBody = false;
String currentSender = "";

void setup() {
  // 1. Initialize Communication
  Serial.begin(PC_BAUD);    // USB to PC
  gsm.begin(GSM_BAUD);      // Hardware Pins 0/1 to SIM800A
  
  // Wait for Serial Monitor (optional, helpful for debugging)
  // while (!Serial); 

  delay(5000); // Give SIM800A time to wake up
  
  Serial.println("[SYSTEM] Initializing Dawa AI GSM Gateway...");

  // 2. SIM800A Handshake
  gsm.println("AT");
  delay(1000);
  
  // 3. Set SMS to Text Mode
  gsm.println("AT+CMGF=1");
  delay(500);
  
  // 4. Configure New Message Indication (CNMI)
  // Mode 2,2 sends SMS content directly to Serial1 +CMT: "number",,"date"
  gsm.println("AT+CNMI=2,2,0,0,0");
  delay(500);

  Serial.println("[SYSTEM] Gateway Online. Monitoring GSM Network...");
  Serial.println("--------------------------------------------------");
}

void loop() {
  // --- PART 1: INBOUND (GSM -> PC) ---
  while (gsm.available()) {
    char c = (char)gsm.read();
    gsmBuffer += c;

    if (c == '\n') {
      gsmBuffer.trim();

      // Check if this line is an SMS header
      // Format: +CMT: "+257XXXXXXX","","26/05/12,12:00:00+00"
      if (gsmBuffer.startsWith("+CMT:")) {
        int firstQuote = gsmBuffer.indexOf('"');
        int secondQuote = gsmBuffer.indexOf('"', firstQuote + 1);
        
        if (firstQuote != -1 && secondQuote != -1) {
          currentSender = gsmBuffer.substring(firstQuote + 1, secondQuote);
          isReceivingBody = true; // The NEXT line will be the message text
        }
      } 
      // If we are waiting for the message body
      else if (isReceivingBody && gsmBuffer.length() > 0) {
        // Construct the Dawa AI protocol: MSG|PHONE|TEXT
        Serial.print("MSG|");
        Serial.print(currentSender);
        Serial.print("|");
        Serial.println(gsmBuffer);

        // Reset for next message
        isReceivingBody = false;
        currentSender = "";
      }

      gsmBuffer = ""; // Clear line buffer
    }
  }

  // --- PART 2: OUTBOUND (PC -> GSM) ---
  if (Serial.available()) {
    // Protocol from PC: SEND|PHONE|REPLY_TEXT
    String pcCommand = Serial.readStringUntil('\n');
    pcCommand.trim();

    if (pcCommand.startsWith("SEND|")) {
      int firstPipe = pcCommand.indexOf('|');
      int secondPipe = pcCommand.indexOf('|', firstPipe + 1);

      if (firstPipe != -1 && secondPipe != -1) {
        String phone = pcCommand.substring(firstPipe + 1, secondPipe);
        String message = pcCommand.substring(secondPipe + 1);
        
        sendSMS(phone, message);
      }
    }
  }
}

/**
 * Sends an SMS using standard AT commands.
 */
void sendSMS(String number, String text) {
  Serial.print("[SYSTEM] Sending SMS to ");
  Serial.println(number);

  // 1. Command to send SMS
  gsm.print("AT+CMGS=\"");
  gsm.print(number);
  gsm.println("\"");
  
  delay(500); // Wait for the '>' prompt from SIM800A

  // 2. The Message Body
  gsm.print(text);
  delay(100);

  // 3. CTRL+Z (ASCII 26) to finalize the message
  gsm.write(26); 
  
  // 4. Wait for confirmation from module
  // (In a production environment, you'd check for +CMGS response)
  delay(3000); 

  Serial.println("[SYSTEM] SMS Dispatch Triggered.");
}
