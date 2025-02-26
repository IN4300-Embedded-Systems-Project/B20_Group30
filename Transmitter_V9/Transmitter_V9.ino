#include <SoftwareSerial.h>
#include <TinyGPSPlus.h>
#include <SPI.h>
#include <LoRa.h>

static const int RXPin = 6, TXPin = 7;
static const uint32_t GPSBaud = 9600;

const int csPin = 10;
const int resetPin = 9;
const int irqPin = 2;

const int buttonPin = 4; // Button connected to D4
const int ledPin = 3;    // LED connected to D3
const int gpsLEDPin = 8; // LED connected to D8
const int helpLEDPin = A1; // LED connected for HELP/OK

TinyGPSPlus gps;
SoftwareSerial ss(RXPin, TXPin);

bool needHelp = false; // Flag to control GPS data transmission
bool lastButtonState = HIGH; // Track previous button state
bool ledState = false; // Track LED state

int id = 1;

void setup() {
  Serial.begin(115200);
  ss.begin(GPSBaud);

  pinMode(buttonPin, INPUT_PULLUP);
  pinMode(ledPin, OUTPUT);  // Set LED pin as output
  pinMode(gpsLEDPin, OUTPUT);  // Set LED pin as output
  pinMode(helpLEDPin, OUTPUT);  // Set LED pin as output
  
  LoRa.setPins(csPin, resetPin, irqPin);
  if (!LoRa.begin(433E6)) { 
    Serial.println("LoRa init failed. Check connections.");
    while (true);
  }
  
  Serial.println("GPS and LoRa Ready!");
}

void loop() {
  // Check button press for toggling
  bool currentButtonState = digitalRead(buttonPin);
  if (currentButtonState == LOW && lastButtonState == HIGH) { 
    delay(50); // Debounce delay
    if (digitalRead(buttonPin) == LOW) { 
      needHelp = !needHelp; // Toggle GPS transmission state
      ledState = !ledState;  // Toggle LED state
      digitalWrite(ledPin, ledState ? HIGH : LOW); // Update LED based on GPS state 
      digitalWrite(helpLEDPin, needHelp ? HIGH : LOW); // Update LED based on state HELP/OK
      Serial.println(needHelp ? "Button pressed. Starting GPS transmission for HELP..." 
                              : "Button pressed again. Continouing GPS transmission.");

      // Wait for button release
      while (digitalRead(buttonPin) == LOW);
      delay(50);
    }
  }
  lastButtonState = currentButtonState;

  // Transmit GPS data
  while (ss.available() > 0) {
    if (gps.encode(ss.read())) {
      sendGPSData();
    }
  }
  

  if (millis() > 5000 && gps.charsProcessed() < 10) {
    digitalWrite(gpsLEDPin, HIGH);
    Serial.println(F("No GPS detected: Retrying..."));
    delay(5000); // Wait and retry
    digitalWrite(gpsLEDPin, LOW);
    return;      // Return to loop() so the button can still be checked
  }
}

void sendGPSData() {
  if (gps.location.isValid()) {
    String gpsData = String(id) + "," 
              + String(gps.location.lat(), 6) + "," 
              + String(gps.location.lng(), 6) + "," 
              + (needHelp?"HELP":"OK");
                     
    Serial.println("Sending: " + gpsData);
    
    digitalWrite(ledPin, HIGH);  // Turn LED on while sending data
    LoRa.beginPacket();
    LoRa.print(gpsData);
    LoRa.endPacket();
    digitalWrite(ledPin, LOW);   // Turn LED off after sending data 
    // LED will blink when GPS data is sending
  } else {
    Serial.println(F("Waiting for valid GPS data..."));
    // LED will turn on when waiting for GPS data
  }
}
