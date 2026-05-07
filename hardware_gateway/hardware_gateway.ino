#include <Arduino.h>

// RP2040 Connect Hardware Serial pins: RX = Pin 0, TX = Pin 1
#define gsm Serial1 

String incomingBuffer = "";
bool isReceivingMsg = false;
String currentSender = "";

void setup() {
  Serial.begin(115200);   // To PC
  gsm.begin(9600);        // To SIM800L (Default baud is usually 9600)
  
  delay(3000); // Wait for module power-up
  Serial.println("Initializing Dawa AI GSM Gateway...");
  
  // Basic AT check
  gsm.println("AT");
  delay(500);
  
  // Set SMS to Text Mode
  gsm.println("AT+CMGF=1");
  delay(500);
  
  // Route incoming SMS directly to Serial terminal (+CMT)
  gsm.println("AT+CNMI=2,2,0,0,0");
  delay(500);
  
  Serial.println("Gateway Ready. Waiting for SMS...");
}

void loop() {
  // 1. Listen to GSM Module (Incoming SMS)
  while (gsm.available()) {
    char c = gsm.read();
    incomingBuffer += c;
    
    // Check if we reached the end of a line
    if (c == '\n') {
      incomingBuffer.trim();
      
      // If line starts with +CMT, it's an incoming SMS header
      if (incomingBuffer.startsWith("+CMT:")) {
        // Extract phone number: +CMT: "+257XXXXXXX",...
        int firstQuote = incomingBuffer.indexOf('"');
        int secondQuote = incomingBuffer.indexOf('"', firstQuote + 1);
        if (firstQuote > -1 && secondQuote > -1) {
          currentSender = incomingBuffer.substring(firstQuote + 1, secondQuote);
          isReceivingMsg = true; // Next line will be the actual message
        }
      } 
      // If we are flagged to receive the message body
      else if (isReceivingMsg && incomingBuffer.length() > 0) {
        // Format and send to PC: MSG|+257XXXXXXX|Message text
        Serial.print("MSG|");
        Serial.print(currentSender);
        Serial.print("|");
        Serial.println(incomingBuffer);
        
        // Reset flags
        isReceivingMsg = false;
        currentSender = "";
      }
      
      incomingBuffer = ""; // Clear buffer for next line
    }
  }

  // 2. Listen to PC (Outgoing AI Responses)
  if (Serial.available()) {
    String pcCommand = Serial.readStringUntil('\n');
    pcCommand.trim();
    
    // PC sends: SEND|+257XXXXXXX|AI Reply
    if (pcCommand.startsWith("SEND|")) {
      int firstPipe = pcCommand.indexOf('|');
      int secondPipe = pcCommand.indexOf('|', firstPipe + 1);
      
      if (firstPipe > -1 && secondPipe > -1) {
        String phoneNum = pcCommand.substring(firstPipe + 1, secondPipe);
        String replyText = pcCommand.substring(secondPipe + 1);
        
        sendSMS(phoneNum, replyText);
      }
    }
  }
}

void sendSMS(String number, String text) {
  Serial.print("Sending SMS to ");
  Serial.println(number);
  
  gsm.print("AT+CMGS=\"");
  gsm.print(number);
  gsm.println("\"");
  delay(500);
  
  gsm.print(text);
  delay(500);
  
  gsm.write(26); // Send CTRL+Z
  delay(3000);   // Give the network time to dispatch the message
  
  Serial.println("SMS Dispatch Complete.");
}