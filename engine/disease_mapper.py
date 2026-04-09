"""
AgroCure - Disease Mapper Engine
Maps detected disease labels → treatments, prevention, severity metadata
"""

DISEASE_MAP = {
    # ─── TOMATO ───────────────────────────────────────────────────────────────
    "Tomato___Late_blight": {
        "display_name": "Tomato Late Blight",
        "crop": "Tomato",
        "disease": "Late Blight",
        "pathogen": "Phytophthora infestans (Fungal-like oomycete)",
        "treatment": [
            "Apply Mancozeb (2.5g/L) or Chlorothalonil fungicide every 7 days",
            "Use copper-based fungicides as an alternative",
            "Remove and destroy all infected plant parts immediately",
        ],
        "prevention": [
            "Avoid overhead irrigation; use drip irrigation",
            "Improve field drainage to reduce moisture buildup",
            "Plant resistant varieties (e.g., Mountain Magic, Defiant)",
            "Maintain plant spacing for better air circulation",
        ],
        "organic_option": "Spray diluted neem oil (3ml/L) + baking soda solution weekly",
        "urgency": "HIGH",
    },
    "Tomato___Early_blight": {
        "display_name": "Tomato Early Blight",
        "crop": "Tomato",
        "disease": "Early Blight",
        "pathogen": "Alternaria solani (Fungal)",
        "treatment": [
            "Apply Azoxystrobin or Difenoconazole fungicide",
            "Spray Mancozeb every 10–14 days as preventive",
            "Prune infected lower leaves and dispose safely",
        ],
        "prevention": [
            "Practice crop rotation (avoid solanaceous crops back-to-back)",
            "Mulch soil to prevent spore splash from soil",
            "Water at the base of plants only",
        ],
        "organic_option": "Compost tea spray + copper sulfate solution",
        "urgency": "MEDIUM",
    },
    "Tomato___Bacterial_spot": {
        "display_name": "Tomato Bacterial Spot",
        "crop": "Tomato",
        "disease": "Bacterial Spot",
        "pathogen": "Xanthomonas campestris (Bacterial)",
        "treatment": [
            "Apply copper-based bactericide (copper hydroxide) every 7 days",
            "Use streptomycin sulfate spray in early stages",
            "Remove heavily infected plants to prevent spread",
        ],
        "prevention": [
            "Use certified disease-free seeds",
            "Avoid working in fields when plants are wet",
            "Disinfect tools with 10% bleach solution",
        ],
        "organic_option": "Copper sulfate + lime spray (Bordeaux mixture)",
        "urgency": "MEDIUM",
    },
    "Tomato___healthy": {
        "display_name": "Tomato - Healthy",
        "crop": "Tomato",
        "disease": None,
        "pathogen": None,
        "treatment": [],
        "prevention": [
            "Maintain balanced NPK fertilization",
            "Monitor weekly for early disease signs",
            "Ensure consistent watering schedule",
        ],
        "organic_option": None,
        "urgency": "NONE",
    },

    # ─── POTATO ───────────────────────────────────────────────────────────────
    "Potato___Early_blight": {
        "display_name": "Potato Early Blight",
        "crop": "Potato",
        "disease": "Early Blight",
        "pathogen": "Alternaria solani (Fungal)",
        "treatment": [
            "Apply Chlorothalonil or Mancozeb fungicide",
            "Spray every 7–10 days during humid conditions",
            "Remove infected foliage promptly",
        ],
        "prevention": [
            "Use certified disease-free seed potatoes",
            "Avoid water stress — stressed plants are more susceptible",
            "Rotate with non-solanaceous crops for 2+ years",
        ],
        "organic_option": "Bacillus subtilis-based biocontrol sprays",
        "urgency": "MEDIUM",
    },
    "Potato___Late_blight": {
        "display_name": "Potato Late Blight",
        "crop": "Potato",
        "disease": "Late Blight",
        "pathogen": "Phytophthora infestans (Fungal-like oomycete)",
        "treatment": [
            "Apply Metalaxyl + Mancozeb combination fungicide immediately",
            "Spray every 5–7 days in wet/cool conditions",
            "Kill and remove vines before harvest to prevent tuber infection",
        ],
        "prevention": [
            "Plant resistant varieties (e.g., Sarpo Mira, Defender)",
            "Hill up soil around stems to protect tubers",
            "Avoid late-season irrigation",
        ],
        "organic_option": "Copper-based sprays (Bordeaux mixture) applied preventively",
        "urgency": "HIGH",
    },
    "Potato___healthy": {
        "display_name": "Potato - Healthy",
        "crop": "Potato",
        "disease": None,
        "pathogen": None,
        "treatment": [],
        "prevention": [
            "Hill regularly to cover tubers and prevent greening",
            "Monitor for Colorado potato beetle weekly",
            "Maintain consistent soil moisture",
        ],
        "organic_option": None,
        "urgency": "NONE",
    },

    # ─── CORN (MAIZE) ─────────────────────────────────────────────────────────
    "Corn_(maize)___Common_rust_": {
        "display_name": "Corn Common Rust",
        "crop": "Corn",
        "disease": "Common Rust",
        "pathogen": "Puccinia sorghi (Fungal)",
        "treatment": [
            "Apply Propiconazole or Tebuconazole fungicide at first sign",
            "Early-season application is critical for effectiveness",
        ],
        "prevention": [
            "Plant rust-resistant hybrids where available",
            "Early planting to avoid peak rust season",
            "Monitor fields weekly from tasseling onwards",
        ],
        "organic_option": "Sulfur-based fungicide sprays",
        "urgency": "MEDIUM",
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "display_name": "Corn Northern Leaf Blight",
        "crop": "Corn",
        "disease": "Northern Leaf Blight",
        "pathogen": "Exserohilum turcicum (Fungal)",
        "treatment": [
            "Apply Azoxystrobin or Propiconazole at early tassel stage",
            "Fungicide application most effective before 50% tasseling",
        ],
        "prevention": [
            "Use resistant hybrid corn varieties",
            "Rotate with non-grass crops",
            "Manage crop residue by tillage or decomposition",
        ],
        "organic_option": "Trichoderma-based biocontrol applied at planting",
        "urgency": "MEDIUM",
    },
    "Corn_(maize)___healthy": {
        "display_name": "Corn - Healthy",
        "crop": "Corn",
        "disease": None,
        "pathogen": None,
        "treatment": [],
        "prevention": [
            "Maintain optimal plant population density",
            "Apply nitrogen fertilizer in split doses",
            "Scout for fall armyworm regularly",
        ],
        "organic_option": None,
        "urgency": "NONE",
    },
}


def get_disease_info(label: str) -> dict:
    """
    Returns full disease info for a given model label.
    Falls back gracefully if label not found.
    """
    label_clean = label.strip()
    info = DISEASE_MAP.get(label_clean)

    if info is None:
        # Attempt fuzzy match by checking if label substring exists
        for key in DISEASE_MAP:
            if label_clean.lower() in key.lower() or key.lower() in label_clean.lower():
                info = DISEASE_MAP[key]
                break

    if info is None:
        return {
            "display_name": label_clean.replace("___", " - ").replace("_", " "),
            "crop": "Unknown",
            "disease": label_clean,
            "pathogen": "Unknown",
            "treatment": ["Consult a local agricultural extension officer"],
            "prevention": ["Monitor closely and isolate affected plants"],
            "organic_option": None,
            "urgency": "UNKNOWN",
        }

    return info
