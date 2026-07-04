from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.resource import Architecture, CloudResource
from app.schemas.resource import ArchitectureOut, ArchitectureUpload
from app.services.aws_client import fetch_cost_and_usage

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("/architecture", response_model=ArchitectureOut, status_code=201)
def upload_architecture(payload: ArchitectureUpload, db: Session = Depends(get_db)):
    """Accepts a manually-defined architecture (from JSON, Terraform-export, etc.)."""
    architecture = Architecture(name=payload.name, provider=payload.provider)
    db.add(architecture)
    db.flush()

    for res in payload.resources:
        db.add(
            CloudResource(
                architecture_id=architecture.id,
                name=res.name,
                resource_type=res.resource_type,
                instance_family=res.instance_family,
                region=res.region,
                vcpus=res.vcpus,
                size_gb=res.size_gb,
                storage_type=res.storage_type,
                monthly_network_gb=res.monthly_network_gb,
                utilization=res.utilization,
                quantity=res.quantity,
            )
        )

    db.commit()
    db.refresh(architecture)
    return architecture


@router.get("/architecture/{architecture_id}", response_model=ArchitectureOut)
def get_architecture(architecture_id: str, db: Session = Depends(get_db)):
    architecture = db.query(Architecture).filter(Architecture.id == architecture_id).first()
    if not architecture:
        raise HTTPException(status_code=404, detail="Architecture not found")
    return architecture


@router.get("/aws-sync")
def sync_from_aws(days: int = 30):
    """Pulls recent usage from AWS Cost Explorer (or mock data) for review before import."""
    return fetch_cost_and_usage(days=days)
