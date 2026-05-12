# Dawa AI: Hardware Handshake Test (SIM-less)

This guide helps you verify that your **Arduino Nano RP2040 Connect** and **SIM800A** are communicating correctly before you insert a SIM card or run the full AI server.

## 🔌 Wiring Recap (The "Golden Triangle")

| SIM800A Pin | Nano RP2040 Pin | Notes |
| :--- | :--- | :--- |
| **GND** | **GND** | **Common Ground** (Connect to both Arduino and Power Supply) |
| **TXD** | **Pin 0 (RX)** | Serial from GSM to Arduino |
| **RXD** | **Pin 1 (TX)** | Serial from Arduino to GSM |
| **VCC** | **External 5V (+)** | Use a 2A Power Source (Not the Arduino pin) |

---

## 💻 Arduino Code (Paste this into Arduino IDE)

```cpp
#include <Arduino.h>

/**
 * DAWA AI - Hardware Bridge Test
 * ------------------------------
 * This script allows you to talk directly to the SIM800A using the 
 * Arduino Serial Monitor. It verifies your TX/RX wiring and power.
 */

// RP2040 Hardware Serial on Pins 0/1
#define gsm Serial1 

void setup() {
  // 1. Initialize USB Serial (Communication with your Computer)
  Serial.begin(115200);
  while (!Serial); // Wait for you to open the Serial Monitor
  
  // 2. Initialize Hardware Serial (Communication with the SIM800A)
  // Default baud for SIM800A is usually 9600.
  gsm.begin(9600);
  
  Serial.println("========================================");
  Serial.println("   DAWA AI: HARDWARE HANDSHAKE TEST     ");
  Serial.println("========================================");
  Serial.println("[*] Checking connection to SIM800A...");
  Serial.println("[*] INSTRUCTIONS:");
  Serial.println("    1. Set Serial Monitor to 115200 baud.");
  Serial.println("    2. Set Line Ending to 'Both NL & CR'.");
  Serial.println("    3. Type 'AT' and press Enter.");
  Serial.println("----------------------------------------");
}

void loop() {
  // Read from SIM800A (GSM) and print to Computer (USB)
  if (gsm.available()) {
    char c = gsm.read();
    Serial.write(c);
  }

  // Read from Computer (USB) and send to SIM800A (GSM)
  if (Serial.available()) {
    char c = Serial.read();
    gsm.write(c);
  }
}
```

---

## 🧪 Testing Steps

1.  **Upload:** Upload the code above to your Nano RP2040.
2.  **Monitor:** Open **Tools > Serial Monitor**.
3.  **Config:** Set baud to **115200** and line ending to **Both NL & CR**.
4.  **The Test:**
    *   Type `AT` $\rightarrow$ Expect `OK`.
    *   Type `AT+GSV` $\rightarrow$ Expect the module version name.
    *   Type `AT+CPIN?` $\rightarrow$ Expect `+CME ERROR: SIM not inserted` (This proves the module is alive!).

---

## 🛠️ Troubleshooting

*   **No response?** Swap your TX and RX wires. (Arduino TX $\rightarrow$ GSM RX).
*   **Gibberish text?** Change `gsm.begin(9600);` to `gsm.begin(115200);` in the code and re-upload.
*   **Module keeps resetting?** Your external power supply isn't providing enough current (need 2A). Add a **1000uF capacitor** across the GSM power pins.
