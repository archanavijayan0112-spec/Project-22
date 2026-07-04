"""
Thin wrapper around AWS Cost Explorer, used to auto-populate an architecture
from real account usage instead of a manual upload.

If AWS credentials aren't configured (e.g. local dev, CI, or a demo run),
this falls back to a small mock dataset so the rest of the app remains usable.
"""

import logging
from datetime import date, timedelta

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _mock_usage() -> list[dict]:
    return [
        {"service": "Amazon Elastic Compute Cloud", "region": "us-east-1", "usage_type": "BoxUsage:m5.xlarge", "cost": 142.30, "quantity_hours": 730},
        {"service": "Amazon Elastic Compute Cloud", "region": "us-west-2", "usage_type": "BoxUsage:c5.large", "cost": 54.10, "quantity_hours": 730},
        {"service": "Amazon Simple Storage Service", "region": "us-east-1", "usage_type": "TimedStorage-ByteHrs", "cost": 23.40, "quantity_gb": 1200},
        {"service": "Amazon Relational Database Service", "region": "eu-west-1", "usage_type": "InstanceUsage:db.r5.large", "cost": 98.75, "quantity_hours": 730},
    ]


def fetch_cost_and_usage(days: int = 30) -> dict:
    """
    Fetches cost & usage grouped by service and region for the last `days` days.
    Returns a dict with a `source` field indicating "aws" or "mock".
    """
    settings = get_settings()

    if not settings.aws_credentials_configured:
        logger.info("AWS credentials not configured; returning mock usage data.")
        return {"source": "mock", "results": _mock_usage()}

    try:
        import boto3

        client = boto3.client(
            "ce",
            region_name="us-east-1",  # Cost Explorer is a global/us-east-1 service
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        )

        end = date.today()
        start = end - timedelta(days=days)

        response = client.get_cost_and_usage(
            TimePeriod={"Start": start.isoformat(), "End": end.isoformat()},
            Granularity="MONTHLY",
            Metrics=["UnblendedCost", "UsageQuantity"],
            GroupBy=[
                {"Type": "DIMENSION", "Key": "SERVICE"},
                {"Type": "DIMENSION", "Key": "REGION"},
            ],
        )

        results = []
        for group in response.get("ResultsByTime", [{}])[0].get("Groups", []):
            service, region = group["Keys"]
            results.append(
                {
                    "service": service,
                    "region": region,
                    "cost": float(group["Metrics"]["UnblendedCost"]["Amount"]),
                    "usage_quantity": float(group["Metrics"]["UsageQuantity"]["Amount"]),
                }
            )

        return {"source": "aws", "results": results}

    except Exception as exc:  # noqa: BLE001 - surfaced to the caller/UI, not swallowed silently
        logger.warning("AWS Cost Explorer request failed, falling back to mock data: %s", exc)
        return {"source": "mock", "results": _mock_usage(), "error": str(exc)}
