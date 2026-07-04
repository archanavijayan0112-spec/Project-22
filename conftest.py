import enum
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.database import Base
from app.db.types import GUID


class ProviderEnum(str, enum.Enum):
    aws = "aws"
    azure = "azure"
    gcp = "gcp"


class ResourceTypeEnum(str, enum.Enum):
    compute = "compute"
    storage = "storage"
    network = "network"
    database = "database"


class Architecture(Base):
    """A single uploaded cloud architecture (a snapshot of resources)."""

    __tablename__ = "architectures"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    provider = Column(Enum(ProviderEnum), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resources = relationship("CloudResource", back_populates="architecture", cascade="all, delete-orphan")


class CloudResource(Base):
    """A single resource (instance, storage volume, etc.) within an architecture."""

    __tablename__ = "cloud_resources"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    architecture_id = Column(GUID(), ForeignKey("architectures.id"), nullable=False)

    name = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceTypeEnum), nullable=False)
    instance_family = Column(String, nullable=True)  # e.g. general_purpose, compute_optimized
    region = Column(String, nullable=False)

    vcpus = Column(Integer, nullable=True)
    size_gb = Column(Float, nullable=True)
    storage_type = Column(String, nullable=True)  # ssd, hdd, object_storage
    monthly_network_gb = Column(Float, nullable=True)
    utilization = Column(Float, nullable=True)  # 0.0 - 1.0
    quantity = Column(Integer, default=1)

    architecture = relationship("Architecture", back_populates="resources")
