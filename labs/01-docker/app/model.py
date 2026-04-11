"""Sentiment model wrapper using DistilBERT (ONNX).

Uses ONNX Runtime via the HuggingFace transformers pipeline for
binary sentiment classification (positive/negative).
"""

from transformers import AutoTokenizer
import onnxruntime as ort
import numpy as np

class SentimentModel:
    MODEL_PATH = "/app/model"

    def __init__(self):
        self.is_loaded = False
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_PATH)
            self.session = ort.InferenceSession(f"{self.MODEL_PATH}/model.onnx")
            self.labels = ["negative", "positive"]
            self.is_loaded = True
        except Exception:
            pass

    def predict(self, text: str) -> dict:
        inputs = self.tokenizer(text, return_tensors="np", truncation=True)
        outputs = self.session.run(None, dict(inputs))
        scores = np.exp(outputs[0]) / np.exp(outputs[0]).sum(axis=-1, keepdims=True)
        idx = scores.argmax(axis=-1)[0]
        return {
            "label": self.labels[idx],
            "score": round(float(scores[0][idx]), 4),
        }
    