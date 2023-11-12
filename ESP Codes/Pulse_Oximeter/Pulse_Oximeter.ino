#include<Wire.h>
#include<MAX30100_PulseOximeter.h>
#include <WiFi.h>
#include <WiFiClient.h>
#include <WiFiServer.h>
#include <ThingSpeak.h>

const char* ssid = "WiFi Name";
const char* password = "Password";

WiFiClient client;
WiFiServer server(80);

#define REPORTING_PERIOD_MS 1000

PulseOximeter pox;
uint32_t tsLastReport = 0;

unsigned long myChannelNumber = 12345; // not a string so remove double-quotes
const char* myWriteAPIKey = "write_api_key";

void onBeatDetected() {
    Serial.println("♥ Beat!");
}

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Connect to Wi-Fi network
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.println((WiFi.localIP()));

  // Start the server
  server.begin();
  Serial.println("Server started");
  Serial.print("Initializing pulse oximeter..");
    // Initialize sensor
    if (!pox.begin()) {
        Serial.println("FAILED");
        for(;;);
    } else {
        Serial.println("SUCCESS");
    }
      // Configure sensor to use 7.6mA for LED drive
  pox.setIRLedCurrent(MAX30100_LED_CURR_7_6MA);

    // Register a callback routine
  pox.setOnBeatDetectedCallback(onBeatDetected);
  ThingSpeak.begin(client);
}

void loop() {
    // Read from the sensor
    pox.update();

    // Grab the updated heart rate and SpO2 levels
    if (millis() - tsLastReport > REPORTING_PERIOD_MS) {
        Serial.print("Heart rate:");
        Serial.print(pox.getHeartRate());
        Serial.print("bpm / SpO2:");
        Serial.print(pox.getSpO2());
        Serial.println("%");

        tsLastReport = millis();
    }

    int x = ThingSpeak.writeField(myChannelNumber, 1, pox.getHeartRate(), myWriteAPIKey);
    int y = ThingSpeak.writeField(myChannelNumber, 1, pox.getSpO2(), myWriteAPIKey);
    Serial.print("Channel Update Successful")
}
