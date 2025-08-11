from enum import Enum
from pydantic import BaseModel


class ChannelCreate(BaseModel):
    bot_id: str
    channel_url: str
    channel_token: str


class ChannelUpdate(BaseModel):
    channel_url: str | None = None
    channel_token: str | None = None


class MessageRole(str, Enum):
    CUSTOMER = "customer"
    EMPLOYEE = "employee"
    ASSISTANT = "assistant"


class IncomingMessage(BaseModel):
    message_id: str
    chat_id: str
    text: str
    message_sender: MessageRole


class OutgoingMessage(BaseModel):
    event_type: str
    chat_id: str
    text: str
