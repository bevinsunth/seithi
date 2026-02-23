import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# --- ML Configuration ---
# Zero-Shot Model for Cold Start
ZERO_SHOT_MODEL = "valhalla/distilbart-mnli-12-3"

# Fine-Tuned Model Path (if exists)
FT_MODEL_PATH = os.path.join(os.path.dirname(__file__), "../models/setfit_v1")

# --- The 3 Axes of Seithi ---
# Each axis uses binary zero-shot classification.
# The score is the confidence of the "positive_label" (0.0 → 1.0).

AXIS_OBJECTIVITY = {
    "name": "objectivity",
    "positive_label": "Factual",       # score=1.0 → factual/objective
    "negative_label": "Opinionated",   # score=0.0 → opinionated
    "hypothesis_template": "This article is {}."
}

AXIS_CALM = {
    "name": "calm",
    "positive_label": "Calm",          # score=1.0 → calm, measured
    "negative_label": "Triggering",    # score=0.0 → rage-bait, triggering
    "hypothesis_template": "The tone of this article is {}."
}

AXIS_DEPTH = {
    "name": "depth",
    "positive_label": "Deep",          # score=1.0 → deep dive, substantive
    "negative_label": "Fluffy",        # score=0.0 → fluff, shallow
    "hypothesis_template": "The content depth of this article is {}."
}

# Ordered list of all axes
ALL_AXES = [AXIS_OBJECTIVITY, AXIS_CALM, AXIS_DEPTH]

# --- Filtering Configuration ---
# Enable/disable filtering of articles based on score thresholds
FILTER_ENABLED = False  # Set to True to enable filtering

# Minimum score thresholds (articles must meet ALL to be saved)
FILTER_THRESHOLDS = {
    "objectivity_min": 0.5,   # At least 50% confidence in "Factual"
    "calm_min": 0.4,           # At least 40% confidence in "Calm"
    "depth_min": 0.3,          # At least 30% confidence in "Deep"
}
