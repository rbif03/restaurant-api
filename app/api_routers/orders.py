from fastapi import APIRouter

from models.order import OrderRead

router = APIRouter()


@router("/{user_id}")
def list_orders(user_id: int) -> list[OrderRead]:
    return
