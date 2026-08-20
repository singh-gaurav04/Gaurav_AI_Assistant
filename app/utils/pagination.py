from fastapi import Query
from pydantic import BaseModel

class Pagination(BaseModel):
    page: int
    limit: int

def pagination_params(
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=100),
) -> Pagination:
    return Pagination(page=page, limit=limit)
