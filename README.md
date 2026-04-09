# 🌱 AgroCure — Backend Setup Guide

## Project Structure

```
agrocure/
├── api/
│   └── app.py              ← FastAPI server (all routes)
├── model/
│   ├── predict.py          ← ML inference module
│   └── agrocure_model.h5   ← ⬅️ DROP YOUR COLAB MODEL HERE
├── engine/
│   ├── disease_mapper.py   ← Disease → treatment knowledge base
│   ├── severity.py         ← Severity + health score + outbreak detection
│   └── recommendation.py  ← Crop recommendation engine
├── chatbot/
│   ├── bot.py              ← Chatbot (rule-based + LLM)
│   └── intents.json        ← Chatbot training data
├── utils/
│   ├── preprocessing.py    ← Image preprocessing
│   └── weather_api.py      ← OpenWeatherMap integration
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Run the server
cd api
python app.py
# → Server running at http://localhost:8000
# → API docs at http://localhost:8000/docs
```

---

## 🧠 Colab Model Integration

### Step 1: Train in Colab
Use this template in your notebook:
```python
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

base = MobileNetV2(weights='imagenet', include_top=False, input_shape=(224,224,3))
x = GlobalAveragePooling2D()(base.output)
x = Dense(256, activation='relu')(x)
output = Dense(NUM_CLASSES, activation='softmax')(x)
model = Model(base.input, output)

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(train_gen, epochs=10, validation_data=val_gen)

# Save to Drive
model.save('/content/drive/MyDrive/agrocure_model.h5')
```

### Step 2: Update CLASS_LABELS
In `model/predict.py`, update `CLASS_LABELS` to match your dataset's folder order (alphabetical).

### Step 3: Drop model file
Place `agrocure_model.h5` in the `model/` folder.

---

## 📡 API Endpoints

| Method | Route | Description |
|--------|-------|-------------|
| POST | `/api/scan` | Upload leaf image → disease diagnosis |
| POST | `/api/chat` | Chatbot message |
| GET | `/api/recommend` | Crop recommendations |
| POST | `/api/analytics` | Farm health analytics |
| GET | `/api/weather` | Weather context |

Full interactive docs: `http://localhost:8000/docs`

---

## 🔌 Frontend Integration

All endpoints return JSON. Example scan call from JS:

```javascript
const formData = new FormData();
formData.append('image', file);

const res = await fetch('http://localhost:8000/api/scan', {
  method: 'POST',
  body: formData,
});
const data = await res.json();
// data.diagnosis.disease → "Late Blight"
// data.severity.label → "Severe"
// data.recommendations.treatment → [...]
```
