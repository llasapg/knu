#ifndef AZURE_CLIENT_H
#define AZURE_CLIENT_H

#include <WiFiClientSecure.h>
#include <PubSubClient.h>

#define TWIN_DESIRED_PATCH_TOPIC "$iothub/twin/PATCH/properties/desired/#"
#define TWIN_REPORTED_TOPIC "$iothub/twin/PATCH/properties/reported/"
#define TWIN_GET_TOPIC "$iothub/twin/GET/"

void setupCloud(const char* ssid, const char* pass, const char* host, int port, MQTT_CALLBACK_SIGNATURE);
void maintainConnection(const char* deviceId, const char* host, const char* key, int ttl);
String generate_sas_token(const char* uri, const char* key, const int expiry);

extern PubSubClient mqttClient;

#endif