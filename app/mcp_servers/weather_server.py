import asyncio
import httpx
import sys

from mcp.server.mcpserver import MCPServer


server = MCPServer(
    name="Singapore Travel Weather",
    version="1.0.0",
)


CITY_COORDINATES = {
    "singapore": {
        "latitude": 1.3521,
        "longitude": 103.8198,
    }
}


@server.tool(
    name="get_weather",
    description=(
        "Get current weather conditions and a weather forecast "
        "for Singapore. Use this tool when the user asks about "
        "current or future weather."
    ),
)
async def get_weather(
    city: str,
    forecast_days: int = 3,
) -> str:

    city_key = city.lower().strip()

    if city_key not in CITY_COORDINATES:
        return (
            f"Weather information is not configured for '{city}'. "
            "Currently supported destination: Singapore."
        )

    forecast_days = max(1, min(forecast_days, 7))

    coordinates = CITY_COORDINATES[city_key]

    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "apparent_temperature,"
            "precipitation,"
            "weather_code"
        ),
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_probability_max,"
            "precipitation_sum"
        ),
        "forecast_days": forecast_days,
        "timezone": "auto",
    }

    try:

        async with httpx.AsyncClient(timeout=15) as client:

            response = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params=params,
            )

            response.raise_for_status()

            data = response.json()

    except httpx.HTTPError as exc:

        return (
            "Weather MCP tool could not retrieve current "
            f"weather information: {exc}"
        )

    current = data.get("current", {})
    daily = data.get("daily", {})

    result = []

    result.append(
        f"Weather information for {city.title()}"
    )

    result.append("")
    result.append("Current conditions:")

    result.append(
        f"Temperature: "
        f"{current.get('temperature_2m')} °C"
    )

    result.append(
        f"Feels like: "
        f"{current.get('apparent_temperature')} °C"
    )

    result.append(
        f"Humidity: "
        f"{current.get('relative_humidity_2m')}%"
    )

    result.append(
        f"Precipitation: "
        f"{current.get('precipitation')} mm"
    )

    result.append("")
    result.append("Forecast:")

    dates = daily.get("time", [])

    for i, date in enumerate(dates):

        result.append(
            f"{date}: "
            f"minimum {daily['temperature_2m_min'][i]} °C, "
            f"maximum {daily['temperature_2m_max'][i]} °C, "
            f"rain probability "
            f"{daily['precipitation_probability_max'][i]}%, "
            f"rainfall "
            f"{daily['precipitation_sum'][i]} mm"
        )

    return "\n".join(result)


async def main():

    print(
        "Starting Singapore Travel Weather MCP Server...",
        flush=True,
        file=sys.stderr
    )

    await server.run_stdio_async()


if __name__ == "__main__":
    asyncio.run(main())