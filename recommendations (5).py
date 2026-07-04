"""
Emissions estimation engine.

Methodology (approximates the open-source Cloud Carbon Footprint project):

    energy_kwh = resource_power_draw(kWh) * PUE
    co2_kg     = energy_kwh * grid_intensity(gCO2/kWh) / 1000

Compute power draw is interpolated between the family's min/max watts-per-vCPU
based on assumed utilization, multiplied by vCPU count and hours in a month.
Storage and network use flat per-GB coefficients.
"""

from app.services.carbon_data import get_instance_power, region_intensity

HOURS_PER_MONTH = 730


def _compute_energy_kwh(resource, power_data: dict) -> float:
    family = resource.instance_family or "general_purpose"
    coeffs = power_data["compute_families"].get(family, power_data["compute_families"]["general_purpose"])
    utilization = resource.utilization if resource.utilization is not None else power_data["default_assumed_utilization"]

    watts_per_vcpu = coeffs["min_watts_per_vcpu"] + (
        coeffs["max_watts_per_vcpu"] - coeffs["min_watts_per_vcpu"]
    ) * utilization

    vcpus = resource.vcpus or 1
    watts = watts_per_vcpu * vcpus
    kwh = (watts * HOURS_PER_MONTH) / 1000
    return kwh


def _storage_energy_kwh(resource, power_data: dict) -> float:
    storage_type = resource.storage_type or "ssd"
    watts_per_gb_month = power_data["storage_types"].get(storage_type, power_data["storage_types"]["ssd"])
    size_gb = resource.size_gb or 0
    return watts_per_gb_month * size_gb


def _network_energy_kwh(resource, power_data: dict) -> float:
    kwh_per_gb = power_data["network"]["kwh_per_gb"]
    gb = resource.monthly_network_gb or 0
    return kwh_per_gb * gb


def estimate_resource_energy_kwh(resource) -> float:
    """Total monthly energy (kWh) for a single resource, before PUE is applied."""
    power_data = get_instance_power()

    energy = 0.0
    if resource.resource_type in ("compute", "database"):
        energy += _compute_energy_kwh(resource, power_data)
    if resource.resource_type == "storage" or resource.size_gb:
        energy += _storage_energy_kwh(resource, power_data)
    if resource.monthly_network_gb:
        energy += _network_energy_kwh(resource, power_data)

    quantity = getattr(resource, "quantity", 1) or 1
    return energy * quantity


def estimate_resource_co2_kg(resource, provider: str, region: str | None = None) -> tuple[float, float]:
    """Returns (energy_kwh_with_pue, co2_kg) for a resource in a given provider/region."""
    power_data = get_instance_power()
    pue = power_data["pue_by_provider"].get(provider, 1.15)

    raw_kwh = estimate_resource_energy_kwh(resource)
    energy_with_pue = raw_kwh * pue

    intensity = region_intensity(provider, region or resource.region)
    co2_kg = (energy_with_pue * intensity) / 1000  # gCO2 -> kg

    return energy_with_pue, co2_kg


def estimate_architecture_emissions(resources: list, provider: str) -> dict:
    """Aggregate emissions across all resources in an architecture."""
    breakdown = []
    total_energy = 0.0
    total_co2 = 0.0

    for r in resources:
        energy_kwh, co2_kg = estimate_resource_co2_kg(r, provider)
        total_energy += energy_kwh
        total_co2 += co2_kg
        breakdown.append(
            {
                "resource_id": r.id,
                "resource_name": r.name,
                "resource_type": r.resource_type.value if hasattr(r.resource_type, "value") else r.resource_type,
                "region": r.region,
                "energy_kwh": round(energy_kwh, 4),
                "co2_kg": round(co2_kg, 4),
            }
        )

    return {
        "total_energy_kwh": round(total_energy, 4),
        "total_co2_kg": round(total_co2, 4),
        # EPA-style rough equivalency factors, for intuitive framing only.
        "equivalent_trees_needed": round(total_co2 / 21.0, 2),  # ~21kg CO2 absorbed/tree/year
        "equivalent_km_driven": round(total_co2 / 0.192, 2),  # ~192g CO2/km avg passenger vehicle
        "breakdown": breakdown,
    }
