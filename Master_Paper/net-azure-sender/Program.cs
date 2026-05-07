using Microsoft.Azure.Devices;
using Microsoft.AspNetCore.Mvc;
using net_azure_sender;

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
        var twin = await registryManager.GetTwinAsync(data.DeviceId);
        
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