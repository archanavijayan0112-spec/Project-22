from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.resource import Architecture
from app.schemas.emission import RegionSuggestionResponse
from app.services.region_advisor import suggest_greener_regions

router = APIRouter(prefix="/regions", tags=["regions"])


@router.get("/suggest/{architecture_id}", response_model=RegionSuggestionResponse)
def suggest_regions(architecture_id: str, db: Session = Depends(get_db)):
    architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
    if not architecture:
        raise HTTPException(status_code=404, detail="Architecture not found")
    if not architecture.resources:
        raise HTTPException(status_code=400, detail="Architecture has no resources")

    # Uses the most common region among resources as the "current" baseline.
    regions = [r.region for r in architecture.resources]
    current_region = max(set(regions), key=regions.count)

    result = suggest_greener_regions(architecture.resources, architecture.provider.value, current_region)

    return {
        "architecture_id": architecture.id,
        "current_region": current_region,
        **result,
    }
