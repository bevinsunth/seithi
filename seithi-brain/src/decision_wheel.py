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
        Returns probability distributions for each axis.
        Each axis returns a list of 3 probabilities corresponding to [class_0, class_1, class_2].
        """
        input_text = self._truncate_text(title, text)
        results = {}

        # 1. Epistemic Axis (Truth)
        # Returns: [Opinion_prob, Mixed_prob, Facts_prob]
        results["epistemic_scores"] = self._predict_axis(input_text, AXIS_EPISTEMIC)

        # 2. Emotive Axis (Tone)
        # Returns: [Triggering_prob, Mixed_prob, Calm_prob]
        results["emotive_scores"] = self._predict_axis(input_text, AXIS_EMOTIVE)

        # 3. Density Axis (Depth)
        # Returns: [Fluff_prob, Standard_prob, Deep_prob]
        results["density_scores"] = self._predict_axis(input_text, AXIS_DENSITY)

        return results

    def _predict_axis(self, text, axis_config):
        """
        Helper to run the classifier for a single axis.
        Returns a list of 3 probabilities in the original label order.
        """
        labels = axis_config["labels"]
        template = axis_config.get("hypothesis_template", "This text is {}.")
        
        output = self.classifier(text, labels, hypothesis_template=template, multi_label=False)
        
        # The classifier returns labels and scores sorted by confidence
        # We need to map them back to the original label order
        label_to_score = dict(zip(output['labels'], output['scores']))
        
        # Return probabilities in original order: [label[0], label[1], label[2]]
        return [label_to_score[label] for label in labels]


if __name__ == "__main__":
    # Test Run
    wheel = DecisionWheel()
    
    sample_title = "Scientists discover new exoplanet"
    sample_text = "In a groundbreaking discovery, astronomers have found a planet capable of supporting life. The data is peer-reviewed and confirmed by multiple observatories. This changes everything we know about the universe."
    
    print("Scoring Sample Article...")
    scores = wheel.score_article(sample_title, sample_text)
    print(scores)
