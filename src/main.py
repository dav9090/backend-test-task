from fastapi import FastAPI
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie

# Загружаем переменные окружения
load_dotenv(".test.env")

# Импортируем модели БД
from src.core.database.models.channel import Channel
from src.core.database.models.chat_bot import ChatBot
from src.core.database.models.dialogue import Dialogue

# Импортируем роутеры
from src.app.routers.api.hello_world import router as hello_world_router
from src.app.routers.api.channels import router as channels_router
from src.app.routers.api.webhook import router as webhook_router

app = FastAPI(
    title="ChatBot API",
    description="Полная версия платформы для создания и управления чат ботами",
    version="1.0.0",
)

@app.on_event("startup")
async def startup_event() -> None:
    """Инициализация MongoDB при запуске приложения"""
    try:
        # Подключаемся к MongoDB
        mongo_url = os.getenv("MONGO__URL", "mongodb://localhost:27017/")
        db_name = os.getenv("MONGO__DB_NAME", "mongo_test")

        # print(f"🔌 Подключаюсь к MongoDB: {mongo_url}")
        # print(f"📊 База данных: {db_name}")

        client: AsyncIOMotorClient = AsyncIOMotorClient(mongo_url)

        # Инициализируем Beanie
        await init_beanie(
            database=client[db_name],
            document_models=[Channel, ChatBot, Dialogue],
        )

        # print("✅ MongoDB успешно инициализирована!")

    except Exception:
        # print(f"❌ Ошибка инициализации MongoDB: {e}")
        # print("⚠️  Приложение запустится без БД")
        pass

# Подключаем все роутеры
app.include_router(hello_world_router)
app.include_router(channels_router)
app.include_router(webhook_router)

@app.get("/")
async def root() -> dict:
    return {
        "message": "ChatBot API is running",
        "version": "1.0.0",
        "endpoints": {
            "hello": "/api/hello",
            "channels": "/api/channels",
            "webhook": "/api/webhook/new_message",
        },
    }

@app.get("/api/health")
async def health_check() -> dict:
    return {"status": "healthy", "message": "API is working"}

if __name__ == "__main__":
    import uvicorn

    # print("🚀 Запускаю ChatBot API (полная версия с MongoDB)...")
    # print("📱 Приложение будет доступно по адресу: http://localhost:8000")
    # print("📚 Документация API: http://localhost:8000/docs")
    # print("🔗 Доступные эндпоинты:")
    # print("   • GET  /api/hello - приветствие")
    # print("   • GET  /api/channels - список каналов")
    # print("   • POST /api/channels - создание канала")
    # print("   • GET  /api/channels/{id} - получение канала")
    # print("   • PATCH /api/channels/{id} - обновление канала")
    # print("   • DELETE /api/channels/{id} - удаление канала")
    # print("   • POST /api/webhook/new_message - получение сообщений")
    # print("⏹️  Для остановки нажмите Ctrl+C")
    # print("-" * 50)

    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
