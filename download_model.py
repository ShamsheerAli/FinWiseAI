from sentence_transformers import SentenceTransformer
import os

os.environ["TRANSFORMERS_CACHE"] = "C:\\Users\\shams\\.cache\\huggingface\\hub"
os.environ["HF_HOME"] = "C:\\Users\\shams\\.cache\\huggingface\\hub"

try:
    model = SentenceTransformer('all-mpnet-base-v2')
    print("Model downloaded successfully!")
except Exception as e:
    print(f"Error downloading model: {e}")