"""
AgroCure - Model Prediction Module

╔══════════════════════════════════════════════════════════════════════════════╗
║                        COLAB MODEL INTEGRATION POINT                        ║
║                                                                              ║
║  STEP 1: Train your CNN/MobileNetV2 model in Google Colab using             ║
║          PlantVillage dataset (see training template below)                  ║
║                                                                              ║
║  STEP 2: Export your trained model:                                          ║
║    model.save("agrocure_model.h5")                  # Keras/TF              ║
║    OR torch.save(model.state_dict(), "model.pth")   # PyTorch               ║
║                                                                              ║
║  STEP 3: Download from Colab and place in: model/agrocure_model.h5          ║
║                                                                              ║
║  STEP 4: Update MODEL_PATH and CLASS_LABELS below to match your training    ║
╚══════════════════════════════════════════════════════════════════════════════╝

Colab Training Template (TensorFlow/Keras):

    from tensorflow.keras.applications import MobileNetV2
    from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
    from tensorflow.keras.models import Model

    base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
    x = GlobalAveragePooling2D()(base.output)
    x = Dense(256, activation='relu')(x)
    output = Dense(NUM_CLASSES, activation='softmax')(x)
    model = Model(base.input, output)

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(train_generator, epochs=10, validation_data=val_generator)
    model.save('/content/drive/MyDrive/agrocure_model.h5')
"""

import os
import numpy as np
from pathlib import Path
from typing import Optional

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — UPDATE THESE AFTER COLAB TRAINING
# ─────────────────────────────────────────────────────────────────────────────

MODEL_PATH = Path(__file__).parent / "agrocure_model.h5"

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TODO: Replace with your actual class labels from Colab training        ║
# ║  These must match the order your ImageDataGenerator saw them            ║
# ║  (alphabetical order of folder names in your dataset)                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
CLASS_LABELS = [
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___healthy",
]

# Global model reference (loaded once on startup)
_model = None


# ─────────────────────────────────────────────────────────────────────────────
# MODEL LOADING
# ─────────────────────────────────────────────────────────────────────────────

def load_model():
    """
    Loads the trained model from disk.
    Called once at API startup.
    """
    global _model

    if not MODEL_PATH.exists():
        print(f"[model] ⚠️  Model file not found at {MODEL_PATH}")
        print("[model] Running in DEMO MODE — predictions will be simulated")
        return None

    try:
        import tensorflow as tf
        _model = tf.keras.models.load_model(str(MODEL_PATH))
        print(f"[model] ✅ Model loaded from {MODEL_PATH}")
        return _model
    except Exception as e:
        print(f"[model] ❌ Failed to load model: {e}")
        return None


# ─────────────────────────────────────────────────────────────────────────────
# PREDICTION
# ─────────────────────────────────────────────────────────────────────────────

def predict(image_array: np.ndarray) -> dict:
    """
    Runs inference on a preprocessed image array.

    Args:
        image_array: numpy array of shape (1, 224, 224, 3)

    Returns:
        dict with label, confidence, all_predictions
    """
    global _model

    # ── Demo mode (no model file yet) ────────────────────────────────────────
    if _model is None:
        return _demo_prediction()

    try:
        # Run inference
        predictions = _model.predict(image_array, verbose=0)  # shape: (1, num_classes)
        probs = predictions[0]

        top_idx = int(np.argmax(probs))
        top_label = CLASS_LABELS[top_idx]
        top_confidence = float(probs[top_idx])

        # Top 3 predictions for transparency
        top3_idx = np.argsort(probs)[::-1][:3]
        top3 = [
            {
                "label": CLASS_LABELS[i],
                "confidence": round(float(probs[i]), 4),
            }
            for i in top3_idx
        ]

        return {
            "label": top_label,
            "confidence": round(top_confidence, 4),
            "top3": top3,
            "demo_mode": False,
        }

    except Exception as e:
        print(f"[model] Prediction error: {e}")
        return _demo_prediction()


def _demo_prediction() -> dict:
    """
    Returns a simulated prediction for testing without a trained model.
    """
    import random
    demo_label = random.choice([
        "Tomato___Late_blight",
        "Potato___Early_blight",
        "Corn_(maize)___Common_rust_",
        "Tomato___healthy",
    ])
    demo_confidence = round(random.uniform(0.75, 0.97), 4)

    return {
        "label": demo_label,
        "confidence": demo_confidence,
        "top3": [
            {"label": demo_label, "confidence": demo_confidence},
        ],
        "demo_mode": True,
        "note": "⚠️ Demo mode — place agrocure_model.h5 in model/ folder to enable real predictions",
    }
