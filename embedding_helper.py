import open_clip
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel

from config import CLIP_PATH


# E5 variables:
tok = None
model = None
# Clip variables:
device = None
model_clip = None
tokenizer = None


def initialize_embedding_model(embed_type):
    if embed_type == "E5":
        initialize_e5()
    elif embed_type == "CLIP":
        initialize_clip()


def compute_embeddings(text, embed_type):
    if embed_type == "E5":
        embeddings = compute_e5_embeddings(text)
    elif embed_type == "CLIP":
        embeddings = compute_clip_embeddings(text)
    return embeddings


def initialize_e5() -> None:
    global tok
    global model
    tok = AutoTokenizer.from_pretrained("./models/e5")
    model = AutoModel.from_pretrained("./models/e5")


def compute_e5_embeddings(texts: list[str]) -> np.ndarray:
    # E5 expects "query: ..." or "passage: ..."
    texts = [f"passage: {t}" for t in texts]
    batch = tok(texts, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        out = model(**batch)
        emb = (out.last_hidden_state * batch["attention_mask"].unsqueeze(-1)).sum(1)
        emb = emb / batch["attention_mask"].sum(1, keepdim=True)
        emb = torch.nn.functional.normalize(emb, p=2, dim=1)  # cosine
    return emb.cpu().numpy()  # shape: (N, 768)


def initialize_clip() -> None:
    global device
    global model_clip
    global tokenizer
    device = "cuda" if torch.cuda.is_available() else "cpu"

    model_clip, _, preprocess = open_clip.create_model_and_transforms(
        "ViT-L-14",
        pretrained=CLIP_PATH
    )
    model_clip = model_clip.to(device)
    tokenizer = open_clip.get_tokenizer("ViT-L-14")


def compute_clip_embeddings(texts: list[str]) -> np.ndarray:
    tokens = tokenizer(texts).to(device)
    with torch.no_grad():
        f = model_clip.encode_text(tokens)
        f = torch.nn.functional.normalize(f, dim=-1)
    return f.cpu().numpy()  # (N, 768)

