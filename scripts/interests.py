import asyncio
import httpx

interests = [
    "Путешествия", "Языки", "Дети", "Книги",
    "Музыка", "Психология", "Здоровье",
    "Хобби", "Поиск любви", "Общение с семьей"
]

async def add_all_interests():
    async with httpx.AsyncClient() as client:
        for interest in interests:
            response = await client.post("http://localhost:8000/interests/", json={"name": interest})
            print(response.json())

if __name__ == "__main__":
    asyncio.run(add_all_interests())
