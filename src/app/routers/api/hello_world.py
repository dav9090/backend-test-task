from fastapi import APIRouter

router = APIRouter()


@router.get("/hello")
async def hello_world() -> dict[str, str]:
    return {"message": "Hello World"}
