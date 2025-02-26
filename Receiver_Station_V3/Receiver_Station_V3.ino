#include <SPI.h>
#include <LoRa.h>

const int csPin = 10;
const int resetPin = 9;
const int irqPin = 2;

String receivedData = "";  // Move the buffer outside the loop for better data handling

void setup() {
  Serial.begin(115200);
  while (!Serial);

  LoRa.setPins(csPin, resetPin, irqPin);

  if (!LoRa.begin(433E6)) {  // Ensure you are using the correct frequency
    Serial.println("LoRa init failed. Check connections.");
    while (true);  // Stop the program if LoRa initialization fails
  }

  //Serial.println("LoRa Receiver Ready!");
}

void loop() {
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {  // If there is a packet received
    //Serial.print("Received packet of size: ");
    //Serial.println(packetSize);
    
    // Clear the receivedData buffer before new data is added
    receivedData = ""; 
    
    while (LoRa.available()) {
      receivedData += (char)LoRa.read();  // Collect all available data into the buffer
    }

    // Print the full received data
    //Serial.print("Received: ");
    Serial.println(receivedData);  // Display the complete data

    // Manually clean the LoRa buffer
    LoRa.flush();  // Ensures LoRa internal buffer is cleared
  }

  // Add a small delay to avoid overloading the receiver
  delay(10);
}

