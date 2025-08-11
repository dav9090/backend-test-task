from typing import Any
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from src.app.schemas import IncomingMessage, OutgoingMessage
from src.core.database.models.chat_bot import ChatBot
from src.core.database.models.channel import Channel
from src.core.database.models.dialogue import Dialogue, DialogueMessage, MessageRole
from src.app.services.llm_service import mock_llm_call
from src.app.services.channel_service import post_to_channel

router = APIRouter(prefix="/webhook", tags=["webhook"], dependencies=[Depends(HTTPBearer())])
bearer_scheme = HTTPBearer()


@router.post("/new_message", response_model=OutgoingMessage)
async def receive_webhook(
    msg: IncomingMessage,
    request: Request,
) -> JSONResponse:
    """
    Обрабатывает входящие сообщения из канала.
    """
    # 1) Проверяем токен бота
    credentials: HTTPAuthorizationCredentials | None = await bearer_scheme(request)
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен бота",
        )
    token = credentials.credentials
    bot = await ChatBot.find_one(ChatBot.secret_token == token)
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен бота",
        )

    # 2) Находим канал для бота
    ch = await Channel.find_one(Channel.bot_id == bot.id)
    if not ch:
        raise HTTPException(status_code=404, detail="Channel not found")

    # 3) Берём или создаём диалог для этого бота и чата
    dlg = await Dialogue.find_one(
        Dialogue.chat_bot_id == bot.id,
        Dialogue.chat_id == msg.chat_id,
    )
    if not dlg:
        if not bot.id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Bot ID is None",
            )
        dialogue_data: dict[str, Any] = {
            "chat_bot_id": bot.id,
            "chat_id": msg.chat_id,
            "message_list": [],
        }
        dlg = Dialogue(**dialogue_data)
        await dlg.insert()

    # 4) Проверяем на дубликат по message_id
    existing_message = next((m for m in dlg.message_list if m.message_id == msg.message_id), None)
    if existing_message:
        return JSONResponse(status_code=409, content={"detail": "Duplicate message"})

    # 5) Сохраняем входящее сообщение (включая от сотрудников)
    dlg.message_list.append(
        DialogueMessage(
            message_id=msg.message_id,
            chat_id=msg.chat_id,
            text=msg.text,
            role=MessageRole.USER if msg.message_sender.value == "customer" else MessageRole.EMPLOYEE,
        ),
    )
    await dlg.save()

    # 6) Если сообщение от сотрудника - только сохраняем, не отвечаем
    if msg.message_sender == MessageRole.EMPLOYEE:
        return JSONResponse(status_code=200, content={"detail": "Employee message saved"})

    # 7) Генерируем ответ через LLM
    assistant_response = await mock_llm_call(msg.text, model="dummy")

    # 8) Отправляем ответ в канал
    message_data = {"event_type": "new_message", "chat_id": msg.chat_id, "text": assistant_response}

    success = await post_to_channel(str(ch.channel_url), ch.channel_token, message_data)

    if not success:
        # Логируем ошибку отправки (в реальном проекте используйте proper logging)
        # print(f"Failed to send message to channel for bot {bot.id}")
        pass

    # 9) Сохраняем ответ ассистента в диалог
    dlg.message_list.append(
        DialogueMessage(
            message_id=f"{msg.message_id}-bot",
            chat_id=msg.chat_id,
            text=assistant_response,
            role=MessageRole.ASSISTANT,
        ),
    )
    await dlg.save()

    # 10) Возвращаем OK
    return JSONResponse(status_code=200, content={"detail": "OK"})
