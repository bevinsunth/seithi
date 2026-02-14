from transformers import pipeline
from sentence_transformers import SentenceTransformer
import torch
import nltk
from nltk.tokenize import sent_tokenize
import os
from .config import ZERO_SHOT_MODEL, AXIS_EPISTEMIC, AXIS_EMOTIVE, AXIS_DENSITY

class DecisionWheel:
    def __init__(self):
        """
        Initializes the ML models.
        """
        self.device = 0 if torch.cuda.is_available() else -1
        print(f"Loading Zero-Shot Model: {ZERO_SHOT_MODEL} on device {self.device}...")
        
        self.classifier = pipeline("zero-shot-classification", 
                                   model=ZERO_SHOT_MODEL, 
                                   device=self.device)
        
        # Download NLTK data for sentence tokenization
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

    def _truncate_text(self, title, text, num_sentences=4):
        """
        Optimizes performance by only analyzing Title + First N Sentences.
        """
        sentences = sent_tokenize(text)
        truncated_body = " ".join(sentences[:num_sentences])
        return f"{title}\n\n{truncated_body}"

    def score_article(self, title, text):
        """
        Returns a dictionary of scores (0, 1, 2) for each axis.
        """
        input_text = self._truncate_text(title, text)
        results = {}

        # 1. Epistemic Axis (Truth)
        # Labels: Speculation (0), Mixed (1), Verified Fact (2)
        score = self._predict_axis(input_text, AXIS_EPISTEMIC)
        results["score_factual"] = score

        # 2. Emotive Axis (Tone)
        # Labels: Triggering (0), Edgy (1), Calm (2)
        score = self._predict_axis(input_text, AXIS_EMOTIVE)
        results["score_emotive"] = score

        # 3. Density Axis (Depth)
        # Labels: Fluff (0), Standard (1), Deep Dive (2)
        score = self._predict_axis(input_text, AXIS_DENSITY)
        results["score_density"] = score

        return results

    def _predict_axis(self, text, axis_config):
        """
        Helper to run the classifier for a single axis.
        """
        labels = axis_config["labels"]
        template = axis_config.get("hypothesis_template", "This text is {}.")
        
        output = self.classifier(text, labels, hypothesis_template=template, multi_label=False)
        
        # The output['labels'] are sorted by score, output['scores'] matches that order.
        # We need to find the index of the highest scoring label in our ORIGINAL ordered list.
        # Original: [Label0, Label1, Label2] -> Index is the score (0, 1, or 2)
        
        top_label = output['labels'][0]
        # Return the index (0, 1, or 2)
        return labels.index(top_label)

if __name__ == "__main__":
    # Test Run
    wheel = DecisionWheel()
    
    sample_title = "Scientists discover new exoplanet"
    sample_text = "In a groundbreaking discovery, astronomers have found a planet capable of supporting life. The data is peer-reviewed and confirmed by multiple observatories. This changes everything we know about the universe."
    
    print("Scoring Sample Article...")
    scores = wheel.score_article(sample_title, sample_text)
    print(scores)
