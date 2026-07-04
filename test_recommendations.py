from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.resource import Architecture
from app.schemas.emission import RecommendationResponse
from app.services.recommendations import generate_recommendations

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/{architecture_id}", response_model=RecommendationResponse)
def get_recommendations(architecture_id: str, db: Session = Depends(get_db)):
    architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
    if not architecture:
        raise HTTPException(status_code=404, detail="Architecture not found")
    if not architecture.resources:
        raise HTTPException(status_code=400, detail="Architecture has no resources")

    recs = generate_recommendations(architecture.resources, architecture.provider.value)

    return {"architecture_id": architecture.id, "recommendations": recs}
