from beanie import PydanticObjectId
from fastapi import APIRouter, HTTPException, status, Response

from src.app.schemas import ChannelCreate, ChannelUpdate
from src.core.database.models.channel import Channel

router = APIRouter(prefix="/channels", tags=["channels"])


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_channel(data: ChannelCreate) -> Channel:
    ch = Channel(**data.model_dump())
    await ch.insert()
    return ch


@router.get("/")
async def list_channels() -> list[Channel]:
    return await Channel.find_all().to_list()


@router.get("/{chan_id}")
async def get_channel(chan_id: str) -> Channel:
    c = await Channel.get(PydanticObjectId(chan_id))
    if not c:
        raise HTTPException(status_code=404, detail="Channel not found")
    return c


@router.patch("/{chan_id}")
async def update_channel(chan_id: str, data: ChannelUpdate) -> Channel:
    c = await Channel.get(PydanticObjectId(chan_id))
    if not c:
        raise HTTPException(status_code=404, detail="Channel not found")
    update = data.model_dump(exclude_unset=True)
    for k, v in update.items():
        setattr(c, k, v)
    await c.save()
    return c


@router.delete(
    "/{chan_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
async def delete_channel(chan_id: str) -> Response:
    c = await Channel.get(PydanticObjectId(chan_id))
    if not c:
        raise HTTPException(status_code=404, detail="Channel not found")
    await c.delete()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
