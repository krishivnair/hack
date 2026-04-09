"""
AgroCure - Image Preprocessing Utilities
Handles image loading, resizing, normalization for model input
"""

import io
import base64
from typing import Optional
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# CONFIG — must match your Colab training config
# ─────────────────────────────────────────────────────────────────────────────

IMAGE_SIZE = (224, 224)        # Match MobileNetV2 / ResNet50 input size
NORMALIZE_MEAN = [0.485, 0.456, 0.406]  # ImageNet mean (if using torchvision)
NORMALIZE_STD  = [0.229, 0.224, 0.225]  # ImageNet std


# ─────────────────────────────────────────────────────────────────────────────
# PREPROCESSING
# ─────────────────────────────────────────────────────────────────────────────

def preprocess_image(image_bytes: bytes) -> Optional[np.ndarray]:
    """
    Preprocesses raw image bytes into a normalized numpy array ready for model input.

    ╔══════════════════════════════════════════════════════════════════════╗
    ║  TODO: Adjust preprocessing to match exactly what your Colab        ║
    ║  training pipeline used (normalization values, resize, etc.)        ║
    ╚══════════════════════════════════════════════════════════════════════╝

    Args:
        image_bytes: Raw bytes from uploaded image

    Returns:
        numpy array of shape (1, 224, 224, 3) normalized for model
    """
    try:
        from PIL import Image

        # Load image
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        # Resize to model input size
        img = img.resize(IMAGE_SIZE, Image.LANCZOS)

        # Convert to numpy array
        img_array = np.array(img, dtype=np.float32)

        # ── Normalization ─────────────────────────────────────────────────
        # Option A: Keras MobileNetV2 / ResNet50 style (scale to [-1, 1])
        img_array = img_array / 127.5 - 1.0

        # Option B: ImageNet normalization (use if your Colab used torchvision)
        # img_array = img_array / 255.0
        # img_array = (img_array - NORMALIZE_MEAN) / NORMALIZE_STD

        # Add batch dimension
        img_array = np.expand_dims(img_array, axis=0)  # (1, 224, 224, 3)

        return img_array

    except Exception as e:
        print(f"[preprocessing] Error processing image: {e}")
        return None


def image_bytes_to_base64(image_bytes: bytes) -> str:
    """Converts image bytes to base64 string for API response."""
    return base64.b64encode(image_bytes).decode("utf-8")


def validate_image(image_bytes: bytes, max_size_mb: float = 10.0) -> tuple[bool, str]:
    """
    Validates uploaded image.

    Returns:
        (is_valid, error_message)
    """
    # Size check
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"Image too large ({size_mb:.1f}MB). Max allowed: {max_size_mb}MB"

    # Format check
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(image_bytes))
        if img.format not in ["JPEG", "PNG", "WEBP", "JPG"]:
            return False, f"Unsupported format: {img.format}. Use JPEG, PNG, or WEBP."
    except Exception:
        return False, "Could not read image file. Please upload a valid image."

    return True, ""
