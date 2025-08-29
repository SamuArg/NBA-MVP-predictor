import os
import torch
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv("MONGOURI")

def get_model():
    return torch.load('models/best_model.pt', weights_only=False)
