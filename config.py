
DB_URL = "postgresql://script_runner@localhost:5432/seattle_airbnb_db"
# DB password is handled securely via ~/.pgpass which contains a line like:
#   localhost:5432:seattle_airbnb_db:script_runner:mypasswordhere

EMBED_TYPE = "E5"  # {currently "E5" or "CLIP"}

# This model path is only needed for EMBED_TYPE="CLIP" above:
# Alas you must copy/paste this from output of the download_model_and_data.py
# run.  I'll leave mine in here to give an idea what it looks like, but yours
# will differ and you must run download_model_and_data.py and paste your own:
CLIP_PATH = "./models/models--laion--CLIP-ViT-L-14-laion2B-s32B-b82K/snapshots/1627032197142fbe2a7cfec626f4ced3ae60d07a/open_clip_pytorch_model.bin"
