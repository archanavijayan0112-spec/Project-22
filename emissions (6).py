from app.services.carbon_data import all_regions
from app.services.emissions import estimate_architecture_emissions

# Rough equivalent-region mapping used to compare "similar" geographic locations
# across providers when a resource is hypothetically moved to another cloud.
EQUIVALENT_REGIONS = {
    "us-east": {"aws": "us-east-1", "azure": "eastus", "gcp": "us-east1"},
    "us-west": {"aws": "us-west-2", "azure": "westus2", "gcp": "us-west1"},
    "eu-west": {"aws": "eu-west-1", "azure": "westeurope", "gcp": "europe-west1"},
    "eu-north": {"aws": "eu-north-1", "azure": "swedencentral", "gcp": "europe-north1"},
    "ap-south": {"aws": "ap-south-1", "azure": "southeastasia", "gcp": "asia-south1"},
    "ap-northeast": {"aws": "ap-northeast-1", "azure": "japaneast", "gcp": "asia-northeast1"},
    "sa-east": {"aws": "sa-east-1", "azure": "brazilsouth", "gcp": "southamerica-east1"},
}


def _closest_geo_group(provider: str, region: str) -> str | None:
    for group, mapping in EQUIVALENT_REGIONS.items():
        if mapping.get(provider) == region:
            return group
    return None


def compare_providers(resources: list, provider: str, region: str) -> dict:
    """
    Compares estimated emissions for the given architecture if deployed to the
    geographically closest region on each of AWS, Azure, and GCP.
    """
    geo_group = _closest_geo_group(provider, region)
    comparisons = []

    for candidate_provider in ("aws", "azure", "gcp"):
        if geo_group and geo_group in EQUIVALENT_REGIONS:
            candidate_region = EQUIVALENT_REGIONS[geo_group].get(candidate_provider)
        else:
            candidate_region = region if region in all_regions(candidate_provider) else None

        if not candidate_region:
            continue

        # Temporarily reassign region for calculation purposes without mutating the DB objects.
        original_regions = [r.region for r in resources]
        for r in resources:
            r.region = candidate_region

        result = estimate_architecture_emissions(resources, candidate_provider)

        for r, orig in zip(resources, original_regions):
            r.region = orig

        from app.services.carbon_data import region_intensity

        comparisons.append(
            {
                "provider": candidate_provider,
                "region": candidate_region,
                "grid_intensity_g_per_kwh": region_intensity(candidate_provider, candidate_region),
                "estimated_co2_kg": result["total_co2_kg"],
            }
        )

    greenest = min(comparisons, key=lambda c: c["estimated_co2_kg"]) if comparisons else None

    return {"comparisons": comparisons, "greenest_option": greenest}
