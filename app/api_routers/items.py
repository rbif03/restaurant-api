from fastapi import APIRouter

from models.item import ItemCreate, ItemRead, ItemUpdate

router = APIRouter()


@router.get("/", status_code=200)
def list_items(category=None) -> list[ItemRead]:
    # database logic
    return


@router.get("/{product_id}", status_code=200)
def get_item_by_id(product_id: int) -> ItemRead:
    # database logic
    return


@router.post("/", status_code=201)
def add_item(body: ItemCreate) -> ItemRead:
    # database logic
    return


@router.patch("/{product_id}")
def update_item(product_id: int, body: ItemUpdate) -> ItemRead:
    fields_to_update = body.model_dump(exclude_unset=True)
    # database logic
    return
