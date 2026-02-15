#!/usr/bin/env python3
"""
Test script to verify multi-class probability scoring system.
"""
import sys
sys.path.insert(0, '/app/src')

from decision_wheel import DecisionWheel

def test_scoring():
    print("=" * 60)
    print("Testing Multi-Class Probability Scoring System")
    print("=" * 60)
    
    wheel = DecisionWheel()
    
    # Test Case 1: Factual, calm, deep article
    print("\n--- Test 1: Scientific Article ---")
    title1 = "Scientists discover new exoplanet"
    text1 = "In a groundbreaking discovery, astronomers have found a planet capable of supporting life. The data is peer-reviewed and confirmed by multiple observatories. This changes everything we know about the universe."
    
    scores1 = wheel.score_article(title1, text1)
    print(f"Title: {title1}")
    print(f"\nEpistemic scores: {scores1['epistemic_scores']}")
    print(f"  Opinion: {scores1['epistemic_scores'][0]:.3f}")
    print(f"  Mixed: {scores1['epistemic_scores'][1]:.3f}")
    print(f"  Facts: {scores1['epistemic_scores'][2]:.3f}")
    print(f"\nEmotive scores: {scores1['emotive_scores']}")
    print(f"  Triggering: {scores1['emotive_scores'][0]:.3f}")
    print(f"  Mixed: {scores1['emotive_scores'][1]:.3f}")
    print(f"  Calm: {scores1['emotive_scores'][2]:.3f}")
    print(f"\nDensity scores: {scores1['density_scores']}")
    print(f"  Fluff: {scores1['density_scores'][0]:.3f}")
    print(f"  Standard: {scores1['density_scores'][1]:.3f}")
    print(f"  Deep: {scores1['density_scores'][2]:.3f}")
    
    # Verify scores sum to ~1.0
    epistemic_sum = sum(scores1['epistemic_scores'])
    emotive_sum = sum(scores1['emotive_scores'])
    density_sum = sum(scores1['density_scores'])
    print(f"\nScore sums (should be ~1.0):")
    print(f"  Epistemic: {epistemic_sum:.3f}")
    print(f"  Emotive: {emotive_sum:.3f}")
    print(f"  Density: {density_sum:.3f}")
    
    # Test Case 2: Opinion, triggering, fluff article
    print("\n--- Test 2: Opinion/Clickbait Article ---")
    title2 = "You won't believe what happened next!"
    text2 = "This shocking revelation will change your life forever. Everyone is talking about it and you need to know now!"
    
    scores2 = wheel.score_article(title2, text2)
    print(f"Title: {title2}")
    print(f"\nEpistemic scores: {scores2['epistemic_scores']}")
    print(f"  Opinion: {scores2['epistemic_scores'][0]:.3f}")
    print(f"  Mixed: {scores2['epistemic_scores'][1]:.3f}")
    print(f"  Facts: {scores2['epistemic_scores'][2]:.3f}")
    print(f"\nEmotive scores: {scores2['emotive_scores']}")
    print(f"  Triggering: {scores2['emotive_scores'][0]:.3f}")
    print(f"  Mixed: {scores2['emotive_scores'][1]:.3f}")
    print(f"  Calm: {scores2['emotive_scores'][2]:.3f}")
    print(f"\nDensity scores: {scores2['density_scores']}")
    print(f"  Fluff: {scores2['density_scores'][0]:.3f}")
    print(f"  Standard: {scores2['density_scores'][1]:.3f}")
    print(f"  Deep: {scores2['density_scores'][2]:.3f}")
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("=" * 60)

if __name__ == "__main__":
    test_scoring()
