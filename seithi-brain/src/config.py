import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- Database Configuration ---
DB_NAME = os.getenv("POSTGRES_DB", "seithi")
DB_USER = os.getenv("POSTGRES_USER", "seithi_user")
DB_PASS = os.getenv("POSTGRES_PASSWORD", "")
DB_HOST = os.getenv("POSTGRES_HOST", "localhost")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- ML Configuration ---
# Zero-Shot Model for Cold Start
ZERO_SHOT_MODEL = "valhalla/distilbart-mnli-12-3"

# Fine-Tuned Model Path (if exists)
FT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/setfit_v1")

# --- The 3 Axes of Seithi ---
# Labels must be ordered: 0 -> 1 -> 2

AXIS_EPISTEMIC = {
    "name": "epistemic",
    "labels": ["Opinion", "Opinion and Facts", "Facts"],
    "hypothesis_template": "This article is based on {}."
}

AXIS_EMOTIVE = {
    "name": "emotive",
    "labels": ["Triggering", "Calm and Triggering", "Calm"],
    "hypothesis_template": "The tone of this article is {}."
}

AXIS_DENSITY = {
    "name": "density",
    "labels": ["Fluff", "Standard", "Deep Dive"],
    "hypothesis_template": "This article is best described as {}."
}

# Mapping for Zero-Shot
ALL_AXES = [AXIS_EPISTEMIC, AXIS_EMOTIVE, AXIS_DENSITY]

# --- Filtering Configuration ---
# Enable/disable filtering of articles based on probability thresholds
FILTER_ENABLED = False  # Set to True to enable filtering

# Minimum probability thresholds for desired classes
# Articles must meet ALL specified thresholds to be saved
FILTER_THRESHOLDS = {
    # Epistemic axis: Require high confidence in "Facts" (index 2)
    "epistemic_facts_min": 0.5,      # At least 50% confidence in "Facts"
    
    # Emotive axis: Require high confidence in "Calm" (index 2)
    "emotive_calm_min": 0.4,         # At least 40% confidence in "Calm"
    
    # Density axis: Require high confidence in "Deep" (index 2)
    "density_deep_min": 0.3          # At least 30% confidence in "Deep Dive"
}
