from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from backend.database import submit_ranking, get_top_rankings

router = APIRouter()

class RankingSubmit(BaseModel):
    name: str
    time: float

@router.post("/ranking/submit")
async def add_ranking(data: RankingSubmit):
    if not data.name or len(data.name) > 20:
        raise HTTPException(status_code=400, detail="Invalid name")
    submit_ranking(data.name, data.time)
    return {"message": "Ranking submitted"}

@router.get("/ranking/list")
async def list_rankings():
    rankings = get_top_rankings()
    return rankings
