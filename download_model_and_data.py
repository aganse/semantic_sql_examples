import kagglehub
import open_clip
from transformers import AutoTokenizer, AutoModel


print("Note: these models are downloaded once from HuggingFace's HF Hub.")
print("  This does mean that at times of high usage this may be slow, which")
print("  is ok to me because I don't wish to pay!  That's all the following")
print("  warning is saying.  No other HF Hub access after this.")
# "Warning: You are sending unauthenticated requests to the HF Hub.
# Please set a HF_TOKEN to enable higher rate limits and faster downloads."

# Download OpenCLIP model and save locally
# model_cfg = open_clip.get_pretrained_cfg("ViT-B-32", "laion2b_s34b_b79k")
# path = open_clip.download_pretrained(model_cfg)
path = open_clip.download_pretrained(
    open_clip.get_pretrained_cfg(
        "ViT-L-14",
        "laion2b_s32b_b82k"
        # "ViT-B-32",
        # "laion2b_s34b_b79k"
    ),
    cache_dir="./models"
)
print(f"\n\n Paste this into your config.py CLIP_PATH:\nOpenCLIP model saved locally to {path}\n\n")

# Download E5 tokenizer and model from HuggingFace and save locally
AutoTokenizer.from_pretrained("intfloat/e5-base-v2").save_pretrained("./models/e5")
AutoModel.from_pretrained("intfloat/e5-base-v2").save_pretrained("./models/e5")
print("E5 model and tokenizer saved locally to ./models/e5")

# Download latest dataset version from Kaggle
path = kagglehub.dataset_download("airbnb/seattle")
print(f"Kaggle airbnb/seattle dataset saved locally to {path}")
# path is ~/.cache/kagglehub/datasets/airbnb/seattle/versions/2 as of this
# writing so that's what's hardwired in etl_data.py module.
