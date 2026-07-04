from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ResourceIn(BaseModel):
    name: str
    resource_type: Literal["compute", "storage", "network", "database"]
    instance_family: Optional[str] = Field(
        default="general_purpose",
        description="One of: general_purpose, compute_optimized, memory_optimized, "
        "storage_optimized, burstable, gpu_accelerated",
    )
    region: str
    vcpus: Optional[int] = None
    size_gb: Optional[float] = None
    storage_type: Optional[Literal["ssd", "hdd", "object_storage"]] = "ssd"
    monthly_network_gb: Optional[float] = 0
    utilization: Optional[float] = Field(default=None, ge=0, le=1)
    quantity: int = 1


class ArchitectureUpload(BaseModel):
    name: str
    provider: Literal["aws", "azure", "gcp"]
    resources: list[ResourceIn]


class ResourceOut(ResourceIn):
    id: UUID
    architecture_id: UUID

    class Config:
        from_attributes = True


class ArchitectureOut(BaseModel):
    id: UUID
    name: str
    provider: str
    resources: list[ResourceOut]

    class Config:
        from_attributes = True
