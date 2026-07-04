from app.services.emissions import estimate_resource_co2_kg

LOW_UTILIZATION_THRESHOLD = 0.15
HIGH_UTILIZATION_THRESHOLD = 0.85
OVERSIZED_STORAGE_GB = 500


def generate_recommendations(resources: list, provider: str) -> list[dict]:
    """
    Rule-based recommendations. Each rule estimates the CO2 impact of the
    suggested change by recomputing emissions under a modified assumption.
    """
    recommendations = []

    for r in resources:
        _, baseline_co2 = estimate_resource_co2_kg(r, provider)

        # Rule 1: rightsizing chronically under-utilized compute
        if r.resource_type in ("compute", "database") and (r.utilization or 0) < LOW_UTILIZATION_THRESHOLD:
            original_util = r.utilization
            r.utilization = 0.5  # simulate rightsizing to a smaller, well-utilized instance
            _, resized_co2 = estimate_resource_co2_kg(r, provider)
            r.utilization = original_util
            savings = max(baseline_co2 - resized_co2, 0)
            recommendations.append(
                {
                    "resource_name": r.name,
                    "category": "Rightsizing",
                    "message": (
                        f"'{r.name}' is running at low utilization "
                        f"({(r.utilization or 0) * 100:.0f}%). Consider downsizing the instance "
                        "or consolidating workloads onto fewer, better-utilized instances."
                    ),
                    "estimated_co2_savings_kg": round(savings, 4),
                }
            )

        # Rule 2: scheduling non-critical/burstable workloads for low-carbon hours
        if r.instance_family == "burstable":
            recommendations.append(
                {
                    "resource_name": r.name,
                    "category": "Carbon-aware scheduling",
                    "message": (
                        f"'{r.name}' looks like a non-critical/burstable workload. Scheduling it "
                        "during hours of lower grid carbon intensity in its region can cut its "
                        "effective emissions without any infrastructure change."
                    ),
                    "estimated_co2_savings_kg": round(baseline_co2 * 0.15, 4),
                }
            )

        # Rule 3: oversized / cold storage on expensive-to-run tiers
        if r.resource_type == "storage" and (r.size_gb or 0) > OVERSIZED_STORAGE_GB and r.storage_type == "ssd":
            original_type = r.storage_type
            r.storage_type = "object_storage"
            _, tiered_co2 = estimate_resource_co2_kg(r, provider)
            r.storage_type = original_type
            savings = max(baseline_co2 - tiered_co2, 0)
            recommendations.append(
                {
                    "resource_name": r.name,
                    "category": "Storage tiering",
                    "message": (
                        f"'{r.name}' is {r.size_gb:.0f}GB on SSD-backed storage. If this data is "
                        "infrequently accessed, moving it to object/cold storage reduces energy draw "
                        "significantly."
                    ),
                    "estimated_co2_savings_kg": round(savings, 4),
                }
            )

        # Rule 4: high network egress
        if (r.monthly_network_gb or 0) > 1000:
            recommendations.append(
                {
                    "resource_name": r.name,
                    "category": "Network optimization",
                    "message": (
                        f"'{r.name}' transfers {r.monthly_network_gb:.0f}GB/month. Adding a CDN/cache "
                        "layer or compressing payloads can meaningfully cut data-transfer energy use."
                    ),
                    "estimated_co2_savings_kg": round(baseline_co2 * 0.08, 4),
                }
            )

    return recommendations
