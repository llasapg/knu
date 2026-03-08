#include "AzureClient.h"
#include <WiFi.h>
#include <time.h>
#include <mbedtls/md.h>
#include <mbedtls/base64.h>

WiFiClientSecure secureClient;
PubSubClient mqttClient(secureClient);

String url_encode(String str) {
  String encoded = "";
  for (int i = 0; i < str.length(); i++) {
    char c = str.charAt(i);
    if (isalnum(c) || c == '-' || c == '_' || c == '.' || c == '~') encoded += c;
    else {
      encoded += '%';
      char buf[3];
      sprintf(buf, "%.2X", (unsigned char)c);
      encoded += buf;
    }
  }
  return encoded;
}

String generate_sas_token(const char* uri, const char* key, const int expiry) {
  unsigned long expiryTime = time(NULL) + expiry;
  String stringToSign = url_encode(uri) + "\n" + String(expiryTime);
  size_t dlen = 0;
  mbedtls_base64_decode(NULL, 0, &dlen, (const unsigned char*)key, strlen(key));
  unsigned char decodedKey[dlen];
  mbedtls_base64_decode(decodedKey, dlen, &dlen, (const unsigned char*)key, strlen(key));
  unsigned char hash[32];
  mbedtls_md_context_t ctx;
  mbedtls_md_init(&ctx);
  mbedtls_md_setup(&ctx, mbedtls_md_info_from_type(MBEDTLS_MD_SHA256), 1);
  mbedtls_md_hmac_starts(&ctx, decodedKey, dlen);
  mbedtls_md_hmac_update(&ctx, (const unsigned char*)stringToSign.c_str(), stringToSign.length());
  mbedtls_md_hmac_finish(&ctx, hash);
  mbedtls_md_free(&ctx);
  size_t elen = 0;
  mbedtls_base64_encode(NULL, 0, &elen, hash, 32);
  unsigned char encodedHash[elen];
  mbedtls_base64_encode(encodedHash, elen, &elen, hash, 32);
  return "SharedAccessSignature sr=" + url_encode(uri) + "&sig=" + url_encode((char*)encodedHash) + "&se=" + String(expiryTime);
}

void setupCloud(const char* ssid, const char* pass, const char* host, int port) {
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  configTime(2 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) delay(500);
  secureClient.setInsecure();
  mqttClient.setServer(host, port);
}

void maintainConnection(const char* deviceId, const char* host, const char* key, int ttl, const char* subTopic) {
  if (!mqttClient.connected()) {
    String uri = String(host) + "/devices/" + String(deviceId);
    String sas = generate_sas_token(uri.c_str(), key, ttl);
    String user = String(host) + "/" + String(deviceId) + "/?api-version=2021-04-12";
    if (mqttClient.connect(deviceId, user.c_str(), sas.c_str())) {
      mqttClient.subscribe(subTopic);
    }
  }
}

void setupCloud(const char* ssid, const char* pass, const char* host, int port, MQTT_CALLBACK_SIGNATURE) {
  WiFi.begin(ssid, pass);
  while (WiFi.status() != WL_CONNECTED) delay(500);
  configTime(2 * 3600, 0, "pool.ntp.org", "time.nist.gov");
  struct tm timeinfo;
  while (!getLocalTime(&timeinfo)) delay(500);
  secureClient.setInsecure();
  mqttClient.setServer(host, port);
  mqttClient.setCallback(callback);
}

bool maintainConnection(const char* deviceId, const char* host, const char* key, int ttl) {
  // If already connected, just return true
  if (mqttClient.connected()) {
    return true;
  }

  // Attempt to connect
  Serial.println("Attempting MQTT connection...");
  String uri = String(host) + "/devices/" + String(deviceId);
  String sas = generate_sas_token(uri.c_str(), key, ttl);
  String user = String(host) + "/" + String(deviceId) + "/?api-version=2021-04-12";

  if (mqttClient.connect(deviceId, user.c_str(), sas.c_str())) {
    Serial.println("Connected to Azure IoT Hub");

    // Subscribe to Twin updates
    bool s1 = mqttClient.subscribe(TWIN_DESIRED_PATCH_TOPIC);

    // Subscribe to C2D messages
    String subTopic = "devices/" + String(deviceId) + "/messages/devicebound/#";
    bool s2 = mqttClient.subscribe(subTopic.c_str());

    Serial.printf("Subscriptions: Twin=%s, C2D=%s\n", s1 ? "OK" : "FAIL", s2 ? "OK" : "FAIL");

    return true;
  }

  Serial.print("Connection failed, rc=");
  Serial.println(mqttClient.state());
  return false;
}