import asyncio
class WeatherService:
    def get_temperature(self):
        return 20

    async def get_temperature_async(self):
        await asyncio.sleep(0.01)
        return 20