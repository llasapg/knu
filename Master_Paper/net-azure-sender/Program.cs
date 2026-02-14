using Microsoft.Azure.Devices;
using Microsoft.Azure.Devices.Shared;
using Microsoft.AspNetCore.Mvc;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

var iotHubConnectionString = builder.Configuration["IOTHUB_SERVICE_STR"];
builder.Services.AddSingleton(RegistryManager.CreateFromConnectionString(iotHubConnectionString));

var app = builder.Build();


app.MapPost("/api/iot/update-twin", async (
    [FromBody] TwinUpdateDto data,
    [FromServices] RegistryManager registryManager) =>
{
    try
    {
        // 1. Получаем текущий твин девайса
        var twin = await registryManager.GetTwinAsync(data.DeviceId);

        // 2. Формируем патч желаемых свойств (desired)
        var patch = new
        {
            properties = new
            {
                desired = new
                {
                    model_threshold = data.Threshold,
                    model_url = data.ModelUrl,
                    min_vals = data.MinVals,
                    max_vals = data.MaxVals,
                    updated_at = DateTimeOffset.UtcNow.ToUnixTimeSeconds(),
                    source = "python_ml_service"
                }
            }
        };

        // 3. Отправляем обновление в Azure
        await registryManager.UpdateTwinAsync(data.DeviceId,
            Newtonsoft.Json.JsonConvert.SerializeObject(patch),
            twin.ETag);

        Console.WriteLine($"[SUCCESS] Twin updated for {data.DeviceId}");
        return Results.Ok(new { status = "success", deviceId = data.DeviceId });
    }
    catch (Exception ex)
    {
        Console.WriteLine($"[ERROR] Azure SDK failed: {ex.Message}");
        return Results.Problem(ex.Message);
    }
});

app.Run();

// DTO для приема данных
public record TwinUpdateDto(
    [property: JsonPropertyName("deviceId")] string DeviceId,
    [property: JsonPropertyName("threshold")] double Threshold,
    [property: JsonPropertyName("modelUrl")] string ModelUrl,
    [property: JsonPropertyName("minVals")] double[] MinVals,
    [property: JsonPropertyName("maxVals")] double[] MaxVals
);