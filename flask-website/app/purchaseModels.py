
from pydantic import BaseModel

class Purchase(BaseModel):
    id: int
    userID: str
    productID: int
    date: str