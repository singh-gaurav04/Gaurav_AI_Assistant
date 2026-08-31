from fastapi import APIRouter, Response

from app.modules.portfolio.service import get_portfolio_payload

public_router = APIRouter(tags=["Portfolio"])


@public_router.get("/portfolio")
async def portfolio(response: Response):
    response.headers["Cache-Control"] = "public, max-age=60"
    data = await get_portfolio_payload()
    return {"success": True, "data": data}
