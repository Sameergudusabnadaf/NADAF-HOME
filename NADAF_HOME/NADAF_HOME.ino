#include <ArduinoJson.h>
#include <ESP8266HTTPClient.h>
#include <ESP8266WiFi.h>

//===================== WIFI =====================
const char *ssid = "NADAF";
const char *password = "8362006307";

//===================== SERVER =====================
String serverGetUrl = "https://nadafhome.vercel.app/get_states";
String serverPostUrl = "https://nadafhome.vercel.app/update_device";

//===================== TIMERS =====================
unsigned long previousMillis = 0;
const long interval = 2500; // Slower sync to prevent Vercel KV rate limits

unsigned long debounceDelay = 50; // Standard debounce delay

//===================== DEVICE STRUCT =====================
struct Device {
  String id;
  int relayPin;
  int buttonPin;
  String currentState;
  bool lastButtonState;
  unsigned long lastDebounceTime;
  bool lastFlickerableState;
};

//=========================================================
// Relay Pins
// D3 = GPIO0
// D4 = GPIO2
// D5 = GPIO14
// D6 = GPIO12
//
// Button Pins
// D1 = GPIO5
// D2 = GPIO4
// D7 = GPIO13
// D8 = GPIO15
//=========================================================

Device devices[] = {{"light1", 0, 5, "OFF", HIGH, 0, HIGH},
                    {"light2", 2, 4, "OFF", HIGH, 0, HIGH},
                    {"light3", 14, 13, "OFF", HIGH, 0, HIGH},
                    {"hallfan", 12, 15, "OFF", HIGH, 0, HIGH}};

const int numDevices = sizeof(devices) / sizeof(Device);

//=========================================================
// WIFI RECONNECT
//=========================================================
void reconnectWiFi() {

  if (WiFi.status() == WL_CONNECTED)
    return;

  Serial.println("WiFi Lost... Reconnecting");

  WiFi.disconnect();
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("WiFi Reconnected");
}

//=========================================================
// RELAY CONTROL
//=========================================================
void updateRelay(int pin, String state) {

  if (state == "ON") {
    digitalWrite(pin, LOW); // Active LOW Relay
  } else {
    digitalWrite(pin, HIGH);
  }
}

//=========================================================
// SEND STATE TO SERVER
//=========================================================
void sendStateToServer(String id, String state) {

  if (WiFi.status() != WL_CONNECTED)
    return;

  WiFiClientSecure client;
  client.setInsecure(); // Required for HTTPS without certificate validation
  HTTPClient http;

  http.begin(client, serverPostUrl);

  http.addHeader("Content-Type", "application/json");

  StaticJsonDocument<200> doc;

  doc["id"] = id;
  doc["state"] = state;

  String body;
  serializeJson(doc, body);

  int httpCode = http.POST(body);

  if (httpCode > 0) {
    Serial.print("Updated: ");
    Serial.println(id);
  } else {
    Serial.print("POST Error: ");
    Serial.println(httpCode);
  }

  http.end();
}

//=========================================================
// GET STATES FROM SERVER
//=========================================================
void getStatesFromServer() {

  if (WiFi.status() != WL_CONNECTED)
    return;

  WiFiClientSecure client;
  client.setInsecure(); // Required for HTTPS without certificate validation
  HTTPClient http;

  http.begin(client, serverGetUrl);

  int httpCode = http.GET();

  if (httpCode > 0) {

    String payload = http.getString();

    StaticJsonDocument<1024> doc;

    DeserializationError error = deserializeJson(doc, payload);

    if (!error) {

      for (int i = 0; i < numDevices; i++) {

        if (doc.containsKey(devices[i].id)) {

          String serverState = doc[devices[i].id].as<String>();

          if (serverState != devices[i].currentState) {

            devices[i].currentState = serverState;

            updateRelay(devices[i].relayPin, devices[i].currentState);

            Serial.print(devices[i].id);
            Serial.print(" => ");
            Serial.println(serverState);
          }
        }
      }
    }
  }

  http.end();
}

//=========================================================
// BUTTON HANDLER
//=========================================================
void readButtons() {

  for (int i = 0; i < numDevices; i++) {

    bool reading = digitalRead(devices[i].buttonPin);

    // If the switch changed, due to noise or pressing:
    if (reading != devices[i].lastFlickerableState) {
      devices[i].lastDebounceTime = millis();
      devices[i].lastFlickerableState = reading;
    }

    if ((millis() - devices[i].lastDebounceTime) > debounceDelay) {
      // whatever the reading is at, it's been there for longer than the debounce
      // delay, so take it as the actual current state:
      if (reading != devices[i].lastButtonState) {
        devices[i].lastButtonState = reading;

        // only toggle if the new button state is LOW
        if (devices[i].lastButtonState == LOW) {

          Serial.print("Pressed: ");
          Serial.println(devices[i].id);

          if (devices[i].currentState == "OFF")
            devices[i].currentState = "ON";
          else
            devices[i].currentState = "OFF";

          updateRelay(devices[i].relayPin, devices[i].currentState);

          sendStateToServer(devices[i].id, devices[i].currentState);
        }
      }
    }
  }
}

//=========================================================
// SETUP
//=========================================================
void setup() {

  Serial.begin(115200);

  for (int i = 0; i < numDevices; i++) {

    pinMode(devices[i].relayPin, OUTPUT);

    digitalWrite(devices[i].relayPin, HIGH);

    pinMode(devices[i].buttonPin, INPUT_PULLUP);
  }

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.println("Connecting WiFi");

  while (WiFi.status() != WL_CONNECTED) {

    delay(500);
    Serial.print(".");
  }

  Serial.println();
  Serial.println("Connected");
  Serial.println(WiFi.localIP());

  // Restore relay states after restart
  getStatesFromServer();
}

//=========================================================
// LOOP
//=========================================================
void loop() {

  reconnectWiFi();

  readButtons();

  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {

    previousMillis = currentMillis;

    getStatesFromServer();
  }
}