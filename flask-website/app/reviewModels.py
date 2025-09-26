
from pydantic import BaseModel

class Review(BaseModel):
    id: int
    userID: str
    productID: int
    stars: int
    review: str