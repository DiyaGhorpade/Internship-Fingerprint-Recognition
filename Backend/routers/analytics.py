from fastapi import APIRouter
from services.analytics_engine import plot_to_base64

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("")
async def analytics_summary():
    heatmap, freq = plot_to_base64()
    return {
        "heatmap": heatmap,
        "frequency": freq
    }
