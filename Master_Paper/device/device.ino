#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <TensorFlowLite_ESP32.h>
#include "tensorflow/lite/micro/all_ops_resolver.h"
#include "tensorflow/lite/micro/micro_error_reporter.h"
#include "tensorflow/lite/micro/micro_interpreter.h"
#include "tensorflow/lite/schema/schema_generated.h"
#include <HTTPClient.h>
#include "AzureClient.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define I2C_ADDR 0x3C
#define BUTTON_CALIB_PIN 18
#define BUTTON_SEND_PIN 19
#define BUZZER_PIN 5
#define LIGHT_PIN 32
#define DHT_PIN 27
#define DHT_TYPE DHT11

#define LIGHT_PIN_YELLOW 15
#define LIGHT_PIN_RED 17
#define LIGHT_PIN_GREEN 16

#define SEQ_LEN 10
#define FEATURES 3
#define INPUT_DIM (SEQ_LEN * FEATURES)
const int kTensorArenaSize = 10 * 1024;

#define WIFI_SSID "IPhone_Y"
#define WIFI_PASSWORD "11111112"
#define IOTHUB_HOSTNAME "knu2026.azure-devices.net"
#define DEVICE_ID "test_1"
#define DEVICE_KEY "KiYa9rY5JUhPBXfWcVrmiBmMfPI2tkS/iw9sI4pDEq4="
#define MQTT_PORT 8883
#define SAS_TOKEN_TTL_SECS 3600
#define D2C_TOPIC "devices/test_1/messages/events/"

uint8_t tensor_arena[kTensorArenaSize];
const tflite::Model* tfl_model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* model_input = nullptr;
TfLiteTensor* model_output = nullptr;
tflite::ErrorReporter* error_reporter = nullptr;

uint8_t* model_buffer = nullptr;
size_t   model_buffer_len = 0;
float smartiot_model_threshold = 0.05f;
float smartiot_model_min_vals[FEATURES] = {0};
float smartiot_model_max_vals[FEATURES] = {1};

String g_modelUrl = "";   // filled from twin GET response

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
DHT dht(DHT_PIN, DHT_TYPE, 40);

bool isCalibrating = false;
bool isAnomalyMode = false;
bool inAnomalyState = false;
int lightValue = 0;
float temp = 0.0, hum = 0.0;
unsigned long lastRead = 0;
unsigned long lastCalibSend = 0;
unsigned long lastBlink = 0;
bool blinkState = false;
float currentThreshold = 0.05;
float sensor_history[SEQ_LEN][FEATURES];

// ── called by PubSubClient for every incoming MQTT message ──────────────────
void messageCallback(char* topic, byte* payload, unsigned int length) {
  // We only care about the twin GET response to grab model_url
  if (strstr(topic, "$iothub/twin/res") == nullptr) return;

  char msg[length + 1];
  memcpy(msg, payload, length);
  msg[length] = '\0';

  DynamicJsonDocument doc(8192);
  if (deserializeJson(doc, msg) != DeserializationError::Ok) return;

  // Twin GET body: {"desired":{...},"reported":{...}}
  JsonObject desired = doc["desired"];
  if (desired.isNull()) return;

  if (desired.containsKey("model_url")) {
    g_modelUrl = desired["model_url"].as<String>();
    // always use .bin
    if (g_modelUrl.endsWith("model_data.h"))
      g_modelUrl.replace("model_data.h", "model.bin");
    Serial.printf("[TWIN] model_url = %s\n", g_modelUrl.c_str());
  }
  if (desired.containsKey("model_threshold"))
    currentThreshold = desired["model_threshold"].as<float>();
}

// ── download model.bin and parse binary payload ─────────────────────────────
bool downloadModel() {
  if (g_modelUrl.length() == 0) {
    Serial.println("[MODEL] No URL, skip");
    return false;
  }
  Serial.printf("[MODEL] GET %s\n", g_modelUrl.c_str());

  HTTPClient http;
  http.begin(g_modelUrl);
  int code = http.GET();
  if (code != HTTP_CODE_OK) {
    Serial.printf("[MODEL] HTTP %d\n", code);
    http.end(); return false;
  }

  WiFiClient* stream = http.getStreamPtr();

  uint8_t lenBuf[4];
  stream->readBytes(lenBuf, 4);
  uint32_t mlen = lenBuf[0] | (lenBuf[1]<<8) | (lenBuf[2]<<16) | (lenBuf[3]<<24);
  Serial.printf("[MODEL] size=%u\n", mlen);

  if (model_buffer) free(model_buffer);
  model_buffer = (uint8_t*)malloc(mlen);
  if (!model_buffer) model_buffer = (uint8_t*)ps_malloc(mlen);
  if (!model_buffer) { http.end(); return false; }

  size_t got = 0;
  while (got < mlen) {
    int n = stream->readBytes(model_buffer + got, mlen - got);
    if (n <= 0) break;
    got += n;
  }
  model_buffer_len = got;

  uint8_t meta[4 + 4*FEATURES + 4*FEATURES];
  stream->readBytes(meta, sizeof(meta));
  memcpy(&smartiot_model_threshold, meta, 4);
  for (int i = 0; i < FEATURES; i++) memcpy(&smartiot_model_min_vals[i], meta + 4 + i*4, 4);
  for (int i = 0; i < FEATURES; i++) memcpy(&smartiot_model_max_vals[i], meta + 4 + FEATURES*4 + i*4, 4);

  http.end();
  Serial.printf("[MODEL] OK threshold=%.4f\n", smartiot_model_threshold);
  return true;
}

// ── display helper ───────────────────────────────────────────────────────────
void updateDisplay(String status, String line1 = "", String line2 = "", String line3 = "") {
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);  display.println(status);
  display.setCursor(0, 20); display.println(line1);
  display.setCursor(0, 40); display.println(line2 + "  " + line3);
  display.display();
}

// ── TFLite init ──────────────────────────────────────────────────────────────
void initTFLite() {
  if (!model_buffer || model_buffer_len < 100) { Serial.println("[TFLITE] No model"); return; }
  static tflite::MicroErrorReporter micro_error_reporter;
  error_reporter = &micro_error_reporter;
  tfl_model = tflite::GetModel(model_buffer);
  if (tfl_model->version() != TFLITE_SCHEMA_VERSION) { Serial.println("[TFLITE] Schema mismatch"); return; }
  static tflite::AllOpsResolver resolver;
  static tflite::MicroInterpreter static_interpreter(tfl_model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
  interpreter = &static_interpreter;
  if (interpreter->AllocateTensors() != kTfLiteOk) { Serial.println("[TFLITE] AllocateTensors failed"); return; }
  model_input  = interpreter->input(0);
  model_output = interpreter->output(0);
  Serial.println("[TFLITE] OK");
}

// ── LED indicator ────────────────────────────────────────────────────────────
// green=16 steady   → NORMAL mode
// yellow=15 blink   → calibration
// red=17 blink      → ANOMALY mode, anomaly active
// green=16 blink    → ANOMALY mode, all OK
void updateLEDs() {
  bool blink = (millis() - lastBlink >= 500);
  if (blink) { blinkState = !blinkState; lastBlink = millis(); }

  if (isCalibrating) {
    digitalWrite(LIGHT_PIN_GREEN,  LOW);
    digitalWrite(LIGHT_PIN_RED,    LOW);
    digitalWrite(LIGHT_PIN_YELLOW, blinkState ? HIGH : LOW);
  } else if (isAnomalyMode) {
    digitalWrite(LIGHT_PIN_YELLOW, LOW);
    if (inAnomalyState) {
      digitalWrite(LIGHT_PIN_GREEN, LOW);
      digitalWrite(LIGHT_PIN_RED,   blinkState ? HIGH : LOW);
    } else {
      digitalWrite(LIGHT_PIN_RED,   LOW);
      digitalWrite(LIGHT_PIN_GREEN, blinkState ? HIGH : LOW);
    }
  } else {
    // NORMAL mode – green steady
    digitalWrite(LIGHT_PIN_YELLOW, LOW);
    digitalWrite(LIGHT_PIN_RED,    LOW);
    digitalWrite(LIGHT_PIN_GREEN,  HIGH);
  }
}

// ── MSE ──────────────────────────────────────────────────────────────────────
float calculateMSE() {
  if (!interpreter) return 0.0f;
  float input_scale = model_input->params.scale;
  int   input_zp    = model_input->params.zero_point;
  float output_scale= model_output->params.scale;
  int   output_zp   = model_output->params.zero_point;
  float norm_input[INPUT_DIM];
  int idx = 0;
  for (int i = 0; i < SEQ_LEN; i++) {
    for (int j = 0; j < FEATURES; j++) {
      float v = sensor_history[i][j];
      float range = smartiot_model_max_vals[j] - smartiot_model_min_vals[j];
      float nv = (range == 0) ? 0 : (v - smartiot_model_min_vals[j]) / range;
      nv = constrain(nv, 0.0f, 1.0f);
      norm_input[idx] = nv;
      int16_t q = (int16_t)round(nv / input_scale) + input_zp;
      model_input->data.int8[idx++] = (int8_t)constrain(q, -128, 127);
    }
  }
  if (interpreter->Invoke() != kTfLiteOk) return 0.0f;
  float mse = 0;
  for (int i = 0; i < INPUT_DIM; i++) {
    float o = (model_output->data.int8[i] - output_zp) * output_scale;
    float d = norm_input[i] - o;
    mse += d * d;
  }
  return mse / INPUT_DIM;
}

// ── SETUP ────────────────────────────────────────────────────────────────────
void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_CALIB_PIN, INPUT_PULLUP);
  pinMode(BUTTON_SEND_PIN,  INPUT_PULLUP);
  pinMode(LIGHT_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(LIGHT_PIN_YELLOW, OUTPUT);
  pinMode(LIGHT_PIN_GREEN, OUTPUT);
  pinMode(LIGHT_PIN_RED, OUTPUT);
  digitalWrite(LIGHT_PIN_YELLOW, LOW);
  digitalWrite(LIGHT_PIN_GREEN, LOW);
  digitalWrite(LIGHT_PIN_RED, LOW);
  dht.begin();
  display.begin(SSD1306_SWITCHCAPVCC, I2C_ADDR);

  updateDisplay("Connecting...");
  setupCloud(WIFI_SSID, WIFI_PASSWORD, IOTHUB_HOSTNAME, MQTT_PORT, messageCallback);
  maintainConnection(DEVICE_ID, IOTHUB_HOSTNAME, DEVICE_KEY, SAS_TOKEN_TTL_SECS);

  // Wait for twin GET response (model_url lands in g_modelUrl via callback)
  updateDisplay("Getting twin...");
  unsigned long t0 = millis();
  while (g_modelUrl.length() == 0 && millis() - t0 < 6000) {
    mqttClient.loop();
    delay(50);
  }

  updateDisplay("Downloading", "model...");
  if (downloadModel()) {
    updateDisplay("Model OK", String(model_buffer_len) + " bytes");
  } else {
    updateDisplay("No model", "run calibration");
  }
  delay(1000);

  initTFLite();
  currentThreshold = smartiot_model_threshold;
}

// ── LOOP ─────────────────────────────────────────────────────────────────────
void loop() {
  maintainConnection(DEVICE_ID, IOTHUB_HOSTNAME, DEVICE_KEY, SAS_TOKEN_TTL_SECS);
  mqttClient.loop();
  updateLEDs();

  if (digitalRead(BUTTON_SEND_PIN) == LOW) {
    delay(200);
    isAnomalyMode = !isAnomalyMode;
    inAnomalyState = false;
    updateDisplay(isAnomalyMode ? "MODE: ANOMALY" : "MODE: NORMAL");
    while (digitalRead(BUTTON_SEND_PIN) == LOW);
  }

  if (millis() - lastRead > 2000) {
    lightValue = analogRead(LIGHT_PIN);
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
      temp = t; hum = h;
      for (int i = 0; i < SEQ_LEN - 1; i++)
        memcpy(sensor_history[i], sensor_history[i+1], sizeof(float)*FEATURES);
      sensor_history[SEQ_LEN-1][0] = lightValue;
      sensor_history[SEQ_LEN-1][1] = temp;
      sensor_history[SEQ_LEN-1][2] = hum;
    }
    lastRead = millis();

    if (!isCalibrating) {
      if (isAnomalyMode) {
        float mse = calculateMSE();
        if (mse > currentThreshold) {
          if (!inAnomalyState) {
            inAnomalyState = true;
            updateDisplay("!! ANOMALY !!", "TRIGGERED", "MSE: " + String(mse, 4));
            String alert = "{\"cmd\":\"ALERT\",\"mse\":" + String(mse, 4) + "}";
            mqttClient.publish(D2C_TOPIC, (const uint8_t*)alert.c_str(), alert.length(), false);
          } else {
            updateDisplay("!! ANOMALY !!", "Active", "MSE: " + String(mse, 4));
          }
        } else {
          if (inAnomalyState) {
            inAnomalyState = false;
            String r = "{\"cmd\":\"RECOVERY\",\"msg\":\"Normal state restored\"}";
            mqttClient.publish(D2C_TOPIC, (const uint8_t*)r.c_str(), r.length(), false);
          }
          updateDisplay("ANOMALY MODE", "Status: Normal", "MSE: " + String(mse, 4), "TR: " + String(currentThreshold, 4));
        }
      } else {
        updateDisplay("NORMAL MODE", "L: " + String(lightValue), "C|H: " + String(temp) + "|" + String(hum));
        String tel = "{\"device_id\":\"test_1\",\"cmd\":\"TELEMETRY\",\"light\":" + String(lightValue)
                     + ",\"temp\":" + String(temp, 1) + ",\"hum\":" + String(hum, 0) + "}";
        mqttClient.publish(D2C_TOPIC, (const uint8_t*)tel.c_str(), tel.length(), false);
      }
    }
  }

  if (digitalRead(BUTTON_CALIB_PIN) == LOW) {
    delay(200);
    isCalibrating = !isCalibrating;
    String cmd = isCalibrating ? "START" : "STOP";
    String msg = "{\"device_id\":\"test_1\",\"cmd\":\"" + cmd + "\"}";
    mqttClient.publish(D2C_TOPIC, (const uint8_t*)msg.c_str(), msg.length(), false);
    if (!isCalibrating) {
      updateDisplay("CALIB STOPPED", "Rebooting...");
      delay(2000);
      ESP.restart();
    } else {
      updateDisplay("CALIB STARTED");
    }
    while (digitalRead(BUTTON_CALIB_PIN) == LOW);
  }

  if (isCalibrating && millis() - lastCalibSend > 2000) {
    lastCalibSend = millis();
    String d = "{\"device_id\":\"test_1\",\"cmd\":\"DATA\",\"values\":["
               + String(lightValue) + "," + String(temp, 1) + "," + String(hum, 0) + "]}";
    mqttClient.publish(D2C_TOPIC, (const uint8_t*)d.c_str(), d.length(), false);
  }
}