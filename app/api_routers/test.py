from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class TestBody(BaseModel):
    name: str
    age: int
    type: str = "request"

@router.post("/")
def test_post(body: TestBody):
    return TestBody(
        name=body.name,
        age=body.age,
        type="response"
    )