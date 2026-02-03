from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

app = FastAPI(title="Medical Diagnosis App")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5501", "http://localhost:5501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------
# Serve Frontend (HTML)
# ---------------------------------------
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def serve_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

# ---------------------------------------
# Load Model ONCE
# ---------------------------------------
model = tf.saved_model.load("./saved_model")
infer = model.signatures["serving_default"]

# Class labels (training order)
class_names = [
    "brain_glioma",
    "brain_meningioma",
    "brain_normal",
    "brain_pituitary",
    "chest_normal",
    "chest_pneumonia"
]

# ---------------------------------------
# Prediction API (called from HTML)
# ---------------------------------------
@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        contents = await file.read()

        # Preprocess image
        img = Image.open(io.BytesIO(contents)).convert("RGB")
        img = img.resize((256, 256))

        img_array = np.array(img).astype(np.float32)
        img_array = np.expand_dims(img_array, axis=0)

        # Inference
        output = infer(tf.constant(img_array))
        probs = output[list(output.keys())[0]].numpy()[0]

        pred_index = int(np.argmax(probs))
        prediction = class_names[pred_index]
        confidence = float(probs[pred_index])

        return {
            "prediction": prediction,
            "confidence": confidence,
            "confidence_percent": round(confidence * 100, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))