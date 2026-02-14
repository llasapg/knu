FROM mcr.microsoft.com/dotnet/sdk:9.0 AS build
WORKDIR /src

# Копируем и восстанавливаем зависимости
COPY ["net-azure-sender.csproj", "./"]
RUN dotnet restore

# Собираем приложение
COPY . .
RUN dotnet publish -c Release -o /out

# Финальный образ
FROM mcr.microsoft.com/dotnet/aspnet:9.0
WORKDIR /app
COPY --from=build /out .

ENTRYPOINT ["dotnet", "net-azure-sender.dll"]