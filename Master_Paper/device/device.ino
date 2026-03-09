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
#include "AzureClient.h"
#include "model_data.h"

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define I2C_ADDR 0x3C
#define BUTTON_CALIB_PIN 18
#define BUTTON_SEND_PIN 19
#define LIGHT_PIN 32
#define DHT_PIN 27
#define DHT_TYPE DHT11

#define SEQ_LEN 10
#define FEATURES 3
#define INPUT_DIM (SEQ_LEN * FEATURES)
const int kTensorArenaSize = 10 * 1024;

#define WIFI_SSID "TP-Link_F2B0"
#define WIFI_PASSWORD "43523986"
#define IOTHUB_HOSTNAME "knu2026.azure-devices.net"
#define DEVICE_ID "test_1"
#define DEVICE_KEY "KiYa9rY5JUhPBXfWcVrmiBmMfPI2tkS/iw9sI4pDEq4="
#define MQTT_PORT 8883
#define SAS_TOKEN_TTL_SECS 3600
#define D2C_TOPIC "devices/test_1/messages/events/"

uint8_t tensor_arena[kTensorArenaSize];
const tflite::Model* model = nullptr;
tflite::MicroInterpreter* interpreter = nullptr;
TfLiteTensor* model_input = nullptr;
TfLiteTensor* model_output = nullptr;
tflite::ErrorReporter* error_reporter = nullptr;

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
DHT dht(DHT_PIN, DHT_TYPE, 40);

bool isCalibrating = false;
bool isAnomalyMode = false;
int lightValue = 0;
float temp = 0.0, hum = 0.0;
unsigned long lastRead = 0;
unsigned long lastCalibSend = 0;

float currentThreshold = 0.05;
float sensor_history[SEQ_LEN][FEATURES];

void updateDisplay(String status, String line1 = "", String line2 = "", String line3 = "") {
  display.clearDisplay();
  display.setTextColor(WHITE);
  display.setTextSize(1);
  display.setCursor(0, 0);
  display.println(status);
  display.setCursor(0, 20);
  display.println(line1);
  display.setCursor(0, 40);
  display.println(line2 + "  " + line3);
  display.display();
}

void messageCallback(char* topic, byte* payload, unsigned int length) {
  char message[length + 1];
  memcpy(message, payload, length);
  message[length] = '\0';
  StaticJsonDocument<512> doc;
  if (deserializeJson(doc, message) == DeserializationError::Ok) {
    if (doc.containsKey("model_threshold")) {
      currentThreshold = doc["model_threshold"];
    }
  }
}

void initTFLite() {
  if (sizeof(smartiot_model) < 100) return;
  static tflite::MicroErrorReporter micro_error_reporter;
  error_reporter = &micro_error_reporter;
  model = tflite::GetModel(smartiot_model);
  if (model->version() != TFLITE_SCHEMA_VERSION) return;
  static tflite::AllOpsResolver resolver;
  static tflite::MicroInterpreter static_interpreter(model, resolver, tensor_arena, kTensorArenaSize, error_reporter);
  interpreter = &static_interpreter;
  if (interpreter->AllocateTensors() != kTfLiteOk) return;
  model_input = interpreter->input(0);
  model_output = interpreter->output(0);
}

float calculateMSE() {
  if (interpreter == nullptr) return 0.0f;

  // 1. Find Local Min and Max for the current window for Min-Max Scaling
  float min_val = sensor_history[0][0];
  float max_val = sensor_history[0][0];

  for (int i = 0; i < SEQ_LEN; i++) {
    for (int j = 0; j < FEATURES; j++) {
      if (sensor_history[i][j] < min_val) min_val = sensor_history[i][j];
      if (sensor_history[i][j] > max_val) max_val = sensor_history[i][j];
    }
  }

  // Extract quantization parameters from the model
  // Note: These are baked into the .tflite model during the conversion process
  float input_scale = model_input->params.scale;
  int input_zero_point = model_input->params.zero_point;
  float output_scale = model_output->params.scale;
  int output_zero_point = model_output->params.zero_point;

  // Buffer to hold normalized float values for accurate MSE calculation later
  float norm_input[INPUT_DIM];
  int idx = 0;

  // 2. Normalize and Quantize (q = round(W_f / S) + Z)
  for (int i = 0; i < SEQ_LEN; i++) {
    for (int j = 0; j < FEATURES; j++) {
      float val = sensor_history[i][j];

      // Min-Max Scaling to [0, 1]
      float norm_val = (max_val - min_val == 0) ? 0 : (val - min_val) / (max_val - min_val);
      norm_input[idx] = norm_val;

      // Quantize to Int8
      int16_t q_val = round(norm_val / input_scale) + input_zero_point;

      // Clamp values to valid int8 range to prevent overflow
      if (q_val > 127) q_val = 127;
      if (q_val < -128) q_val = -128;

      // Write quantized integer directly to model input
      model_input->data.int8[idx++] = (int8_t)q_val;
    }
  }

  // 3. Run Inference on the MCU
  if (interpreter->Invoke() != kTfLiteOk) return 0.0f;

  // 4. Dequantize Output and Calculate Reconstruction Error
  float mse = 0;
  for (int i = 0; i < INPUT_DIM; i++) {
    // Dequantize: float_val = (q_val - Z) * S
    float out_f = (model_output->data.int8[i] - output_zero_point) * output_scale;

    // Calculate difference between original normalized float and reconstructed float
    float diff = norm_input[i] - out_f;
    mse += diff * diff;
  }

  return mse / INPUT_DIM;
}

void setup() {
  Serial.begin(115200);
  pinMode(BUTTON_CALIB_PIN, INPUT_PULLUP);
  pinMode(BUTTON_SEND_PIN, INPUT_PULLUP);
  pinMode(LIGHT_PIN, INPUT);
  dht.begin();
  display.begin(SSD1306_SWITCHCAPVCC, I2C_ADDR);
  initTFLite();
  currentThreshold = smartiot_model_threshold;
  setupCloud(WIFI_SSID, WIFI_PASSWORD, IOTHUB_HOSTNAME, MQTT_PORT, messageCallback);
}

void loop() {
  maintainConnection(DEVICE_ID, IOTHUB_HOSTNAME, DEVICE_KEY, SAS_TOKEN_TTL_SECS);
  mqttClient.loop();

  if (digitalRead(BUTTON_SEND_PIN) == LOW) {
    delay(200);
    isAnomalyMode = !isAnomalyMode;
    updateDisplay(isAnomalyMode ? "MODE: ANOMALY" : "MODE: NORMAL");
    while(digitalRead(BUTTON_SEND_PIN) == LOW);
  }

  if (millis() - lastRead > 2000) {
    lightValue = analogRead(LIGHT_PIN);
    float t = dht.readTemperature();
    float h = dht.readHumidity();
    if (!isnan(t) && !isnan(h)) {
      temp = t; hum = h;
      for(int i = 0; i < SEQ_LEN - 1; i++) {
        memcpy(sensor_history[i], sensor_history[i+1], sizeof(float) * FEATURES);
      }
      sensor_history[SEQ_LEN-1][0] = (float)lightValue;
      sensor_history[SEQ_LEN-1][1] = temp;
      sensor_history[SEQ_LEN-1][2] = hum;
    }
    lastRead = millis();

    if (!isCalibrating) {
      if (isAnomalyMode) {
        float mse = calculateMSE();
        if (mse > currentThreshold) {
          updateDisplay("!! ANOMALY !!", "MSE: " + String(mse, 4), "TR: " + String(currentThreshold, 4));
          String alert = "{\"cmd\":\"ALERT\",\"mse\":" + String(mse, 4) + "}";
          mqttClient.publish(D2C_TOPIC, (const uint8_t*)alert.c_str(), alert.length(), false);
        } else {
          updateDisplay("ANOMALY MODE", "Status: Normal", "MSE: " + String(mse, 4), "TR: " + String(currentThreshold, 4));
        }
      } else {
        updateDisplay("NORMAL MODE", "L: " + String(lightValue), "C|H: " + String(temp) + "|" + String(hum));
        String telemetry = "{\"device_id\":\"test_1\",\"cmd\":\"TELEMETRY\",\"light\":" + String(lightValue) +
                           ",\"temp\":" + String(temp, 1) + ",\"hum\":" + String(hum, 0) + "}";
        mqttClient.publish(D2C_TOPIC, (const uint8_t*)telemetry.c_str(), telemetry.length(), false);
      }
    }
  }

  if (digitalRead(BUTTON_CALIB_PIN) == LOW) {
    delay(200);
    isCalibrating = !isCalibrating;
    String cmd = isCalibrating ? "START" : "STOP";
    String msg = "{\"device_id\":\"test_1\",\"cmd\":\"" + cmd + "\"}";
    mqttClient.publish(D2C_TOPIC, (const uint8_t*)msg.c_str(), msg.length(), false);
    updateDisplay(isCalibrating ? "CALIB STARTED" : "CALIB STOPPED");
    while(digitalRead(BUTTON_CALIB_PIN) == LOW);
  }

  if (isCalibrating && millis() - lastCalibSend > 2000) {
    lastCalibSend = millis();
    String dataMsg = "{\"device_id\":\"test_1\",\"cmd\":\"DATA\",\"values\":["
                     + String(lightValue) + "," + String(temp, 1) + "," + String(hum, 0) + "]}";
    mqttClient.publish(D2C_TOPIC, (const uint8_t*)dataMsg.c_str(), dataMsg.length(), false);
  }
}