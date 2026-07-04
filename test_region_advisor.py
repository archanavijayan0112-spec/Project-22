from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.resource import Architecture
from app.schemas.emission import ArchitectureEmissionSummary
from app.services.emissions import estimate_architecture_emissions

router = APIRouter(prefix="/emissions", tags=["emissions"])


@router.get("/estimate/{architecture_id}", response_model=ArchitectureEmissionSummary)
def estimate_emissions(architecture_id: str, db: Session = Depends(get_db)):
    architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
    if not architecture:
        raise HTTPException(status_code=404, detail="Architecture not found")
    if not architecture.resources:
        raise HTTPException(status_code=400, detail="Architecture has no resources to estimate")

    result = estimate_architecture_emissions(architecture.resources, architecture.provider.value)

    return {
        "architecture_id": architecture.id,
        "architecture_name": architecture.name,
        "provider": architecture.provider.value,
        **result,
    }
