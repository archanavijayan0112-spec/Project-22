from app.services.carbon_data import all_regions, region_intensity
from app.services.emissions import estimate_architecture_emissions


def suggest_greener_regions(resources: list, provider: str, current_region: str, top_n: int = 5) -> dict:
    """
    Re-estimates total emissions for an architecture as if every resource were
    relocated to each candidate region, then ranks candidates by CO2 reduction.
    """
    current = estimate_architecture_emissions(resources, provider)
    current_co2 = current["total_co2_kg"]
    current_intensity = region_intensity(provider, current_region)

    candidates = []
    for region, intensity in all_regions(provider).items():
        if region == current_region:
            continue

        # Emissions scale linearly with grid intensity for a fixed energy profile,
        # so we can re-derive total CO2 without recomputing per-resource energy.
        if current_intensity == 0:
            continue
        projected_co2 = current_co2 * (intensity / current_intensity)
        reduction_pct = ((current_co2 - projected_co2) / current_co2 * 100) if current_co2 else 0

        candidates.append(
            {
                "region": region,
                "grid_intensity_g_per_kwh": intensity,
                "estimated_co2_kg": round(projected_co2, 4),
                "co2_reduction_percent": round(reduction_pct, 2),
            }
        )

    candidates.sort(key=lambda c: c["estimated_co2_kg"])
    greener_only = [c for c in candidates if c["co2_reduction_percent"] > 0]

    return {
        "current_co2_kg": current_co2,
        "suggestions": greener_only[:top_n] if greener_only else candidates[:top_n],
    }
