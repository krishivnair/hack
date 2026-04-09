"""
AgroCure - Crop Recommendation & Profit Optimization Engine
Season/region/condition-aware crop suggestions for Indian farmers
"""

from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CROP KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────────────────────

CROP_DB = {
    "tomato": {
        "name": "Tomato",
        "seasons": ["kharif", "rabi"],
        "soil_types": ["loamy", "sandy loam", "red"],
        "water_need": "medium",
        "growth_days": 75,
        "avg_yield_ton_per_acre": 8,
        "market_price_inr_per_kg": 25,
        "input_cost_inr_per_acre": 20000,
        "profit_potential": "HIGH",
        "drought_tolerant": False,
        "notes": "High-value cash crop; susceptible to Late Blight in humid conditions",
    },
    "potato": {
        "name": "Potato",
        "seasons": ["rabi"],
        "soil_types": ["loamy", "sandy loam"],
        "water_need": "medium",
        "growth_days": 90,
        "avg_yield_ton_per_acre": 10,
        "market_price_inr_per_kg": 15,
        "input_cost_inr_per_acre": 25000,
        "profit_potential": "MEDIUM",
        "drought_tolerant": False,
        "notes": "Requires cool temperatures; excellent storage crop",
    },
    "maize": {
        "name": "Maize (Corn)",
        "seasons": ["kharif", "rabi", "zaid"],
        "soil_types": ["loamy", "clay loam", "black"],
        "water_need": "medium",
        "growth_days": 95,
        "avg_yield_ton_per_acre": 4,
        "market_price_inr_per_kg": 20,
        "input_cost_inr_per_acre": 12000,
        "profit_potential": "MEDIUM",
        "drought_tolerant": True,
        "notes": "Versatile; good for fodder and food; relatively drought tolerant",
    },
    "millet": {
        "name": "Pearl Millet (Bajra)",
        "seasons": ["kharif"],
        "soil_types": ["sandy", "sandy loam", "red"],
        "water_need": "low",
        "growth_days": 75,
        "avg_yield_ton_per_acre": 1.5,
        "market_price_inr_per_kg": 22,
        "input_cost_inr_per_acre": 6000,
        "profit_potential": "LOW",
        "drought_tolerant": True,
        "notes": "Extremely drought-resistant; low input cost; ideal for arid regions",
    },
    "onion": {
        "name": "Onion",
        "seasons": ["rabi", "kharif"],
        "soil_types": ["loamy", "sandy loam", "red"],
        "water_need": "medium",
        "growth_days": 120,
        "avg_yield_ton_per_acre": 10,
        "market_price_inr_per_kg": 20,
        "input_cost_inr_per_acre": 30000,
        "profit_potential": "HIGH",
        "drought_tolerant": False,
        "notes": "High market volatility; profitable in good seasons",
    },
    "groundnut": {
        "name": "Groundnut",
        "seasons": ["kharif", "rabi"],
        "soil_types": ["sandy loam", "red", "loamy"],
        "water_need": "low",
        "growth_days": 110,
        "avg_yield_ton_per_acre": 1.2,
        "market_price_inr_per_kg": 55,
        "input_cost_inr_per_acre": 14000,
        "profit_potential": "HIGH",
        "drought_tolerant": True,
        "notes": "Nitrogen-fixing legume; improves soil; drought-tolerant once established",
    },
    "rice": {
        "name": "Rice (Paddy)",
        "seasons": ["kharif"],
        "soil_types": ["clay", "clay loam", "black"],
        "water_need": "high",
        "growth_days": 120,
        "avg_yield_ton_per_acre": 2.5,
        "market_price_inr_per_kg": 20,
        "input_cost_inr_per_acre": 18000,
        "profit_potential": "MEDIUM",
        "drought_tolerant": False,
        "notes": "Staple crop; requires abundant water; supports MSP",
    },
    "chilli": {
        "name": "Chilli",
        "seasons": ["kharif", "rabi"],
        "soil_types": ["loamy", "sandy loam", "red"],
        "water_need": "medium",
        "growth_days": 130,
        "avg_yield_ton_per_acre": 2.5,
        "market_price_inr_per_kg": 60,
        "input_cost_inr_per_acre": 22000,
        "profit_potential": "HIGH",
        "drought_tolerant": False,
        "notes": "High value spice crop; significant export potential",
    },
}

# ─────────────────────────────────────────────────────────────────────────────
# RECOMMENDATION ENGINE
# ─────────────────────────────────────────────────────────────────────────────

def recommend_crops(
    season: Optional[str] = None,
    soil_type: Optional[str] = None,
    water_availability: Optional[str] = None,   # low / medium / high
    drought_region: bool = False,
    top_n: int = 4,
) -> list[dict]:
    """
    Recommends crops based on farmer's conditions.

    Args:
        season: 'kharif' | 'rabi' | 'zaid'
        soil_type: 'loamy' | 'sandy' | 'clay' | etc.
        water_availability: 'low' | 'medium' | 'high'
        drought_region: True if farmer is in drought-prone area
        top_n: number of recommendations to return

    Returns:
        Ranked list of crop recommendation dicts
    """
    results = []

    for crop_key, crop in CROP_DB.items():
        score = 0

        # Season match
        if season and season.lower() in crop["seasons"]:
            score += 30

        # Soil match
        if soil_type:
            soil_lower = soil_type.lower()
            if any(soil_lower in s for s in crop["soil_types"]):
                score += 25

        # Water availability match
        if water_availability:
            need = crop["water_need"]
            wa = water_availability.lower()
            if wa == "low" and need == "low":
                score += 20
            elif wa == "medium" and need in ["low", "medium"]:
                score += 20
            elif wa == "high":
                score += 20  # All crops viable with high water

        # Drought region bonus
        if drought_region and crop["drought_tolerant"]:
            score += 15

        # Profit bonus
        profit_bonus = {"HIGH": 10, "MEDIUM": 5, "LOW": 0}
        score += profit_bonus.get(crop["profit_potential"], 0)

        # Calculate estimated profit
        estimated_profit = calculate_profit(crop)

        results.append({
            "crop": crop["name"],
            "score": score,
            "profit_potential": crop["profit_potential"],
            "estimated_profit_inr_per_acre": estimated_profit,
            "growth_days": crop["growth_days"],
            "avg_yield": f"{crop['avg_yield_ton_per_acre']} tons/acre",
            "water_need": crop["water_need"],
            "drought_tolerant": crop["drought_tolerant"],
            "notes": crop["notes"],
        })

    # Sort by score descending
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def calculate_profit(crop: dict) -> int:
    """Estimates profit per acre in INR."""
    revenue = crop["avg_yield_ton_per_acre"] * 1000 * crop["market_price_inr_per_kg"]
    profit = revenue - crop["input_cost_inr_per_acre"]
    return max(0, int(profit))
