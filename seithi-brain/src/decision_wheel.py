from transformers import pipeline
import torch
import nltk
from nltk.tokenize import sent_tokenize
from .config import ZERO_SHOT_MODEL, AXIS_OBJECTIVITY, AXIS_CALM, AXIS_DEPTH

class DecisionWheel:
    def __init__(self):
        """
        Initializes the zero-shot classification model.
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
        Returns a single 0.0–1.0 score per axis:
          - objectivity_score: 0 = opinionated, 1 = factual
          - calm_score:        0 = rage-bait, 1 = calm
          - depth_score:       0 = fluff, 1 = deep dive
        """
        input_text = self._truncate_text(title, text)
        return {
            "objectivity_score": self._predict_axis(input_text, AXIS_OBJECTIVITY),
            "calm_score":        self._predict_axis(input_text, AXIS_CALM),
            "depth_score":       self._predict_axis(input_text, AXIS_DEPTH),
        }

    def _predict_axis(self, text, axis_config):
        """
        Runs binary zero-shot classification for one axis.
        Returns the confidence score for the positive label (0.0–1.0).
        """
        labels = [axis_config["negative_label"], axis_config["positive_label"]]
        template = axis_config.get("hypothesis_template", "This text is {}.")

        output = self.classifier(text, labels, hypothesis_template=template, multi_label=False)

        label_to_score = dict(zip(output['labels'], output['scores']))
        return label_to_score[axis_config["positive_label"]]


if __name__ == "__main__":
    # Test Run
    wheel = DecisionWheel()

    sample_title = "Scientists discover new exoplanet"
    sample_text = "In a groundbreaking discovery, astronomers have found a planet capable of supporting life. The data is peer-reviewed and confirmed by multiple observatories. This changes everything we know about the universe."

    print("Scoring Sample Article...")
    scores = wheel.score_article(sample_title, sample_text)
    for name, score in scores.items():
        print(f"  {name}: {score:.3f}")
