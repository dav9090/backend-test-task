from beanie import init_beanie
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorClient

from src.core import settings
from src.core.database.models.chat_bot import ChatBot
from src.core.database.models.dialogue import Dialogue
from src.core.database.models.channel import Channel


async def initialize_database() -> None:
    logger.info("Initialising DB...")

    await init_beanie(
        database=AsyncIOMotorClient(settings.mongo.url).get_database(settings.mongo.db_name),
        document_models=[
            ChatBot,
            Channel,
            Dialogue,
        ],
    )
    logger.success("DB is ready!")
