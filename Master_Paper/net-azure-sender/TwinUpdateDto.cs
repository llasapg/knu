using System.Text.Json.Serialization;

namespace net_azure_sender;

public record TwinUpdateDto(
    [property: JsonPropertyName("deviceId")] string DeviceId,
    [property: JsonPropertyName("threshold")] double Threshold,
    [property: JsonPropertyName("modelUrl")] string ModelUrl,
    [property: JsonPropertyName("minVals")] double[] MinVals,
    [property: JsonPropertyName("maxVals")] double[] MaxVals
);