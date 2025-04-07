var humidityDevice = "IoT6";
var acDevice = "AirConditioner";
var lastState = "";

function getHumidity() {
    var humidity = getDeviceProperty(humidityDevice, "level");

    if (humidity !== null && humidity !== "") {
        return parseFloat(humidity);
    }

    Serial.println("Failed to get humidity");

    return null;
}

function setAirConditioner(state) {
    if (state !== lastState) {
        setDeviceProperty(acDevice, "power", state);
        Serial.println("Air Conditioner " + state);
        lastState = state;
    }
}

function loop() {
    var humidity = getHumidity();

    Serial.println("Humidity: " + humidity);

    if (humidity !== null) {

        if (humidity > 60) {
            setAirConditioner("on");
        } else {
            setAirConditioner("off");
        }
    } else {
        Serial.println("Failed to get humidity data");
    }

    delay(5000);
}