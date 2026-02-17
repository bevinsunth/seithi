package main

import (
	"time"
)

// Article represents a news article with probability scores
type Article struct {
	ID                      string     `json:"id"`
	Title                   string     `json:"title"`
	URL                     string     `json:"url"`
	Domain                  string     `json:"domain"`
	PublishedAt             *time.Time `json:"published_at,omitempty"`
	EpistemicOpinionScore   float64    `json:"epistemic_opinion_score"`
	EpistemicMixedScore     float64    `json:"epistemic_mixed_score"`
	EpistemicFactsScore     float64    `json:"epistemic_facts_score"`
	EmotiveTriggeringScore  float64    `json:"emotive_triggering_score"`
	EmotiveMixedScore       float64    `json:"emotive_mixed_score"`
	EmotiveCalmScore        float64    `json:"emotive_calm_score"`
	DensityFluffScore       float64    `json:"density_fluff_score"`
	DensityStandardScore    float64    `json:"density_standard_score"`
	DensityDeepScore        float64    `json:"density_deep_score"`
}

// FeedbackRequest represents user feedback on article scores
type FeedbackRequest struct {
	ArticleID string `json:"article_id"`
	Axis      string `json:"axis"`
	UserScore int    `json:"user_score"`
}

// ArticlesResponse represents the API response for articles list
type ArticlesResponse struct {
	Articles []Article `json:"articles"`
	Total    int       `json:"total"`
	Limit    int       `json:"limit"`
	Offset   int       `json:"offset"`
}

// StatsResponse represents overall statistics
type StatsResponse struct {
	TotalArticles int     `json:"total_articles"`
	AvgFactsScore float64 `json:"avg_facts_score"`
	AvgCalmScore  float64 `json:"avg_calm_score"`
	AvgDeepScore  float64 `json:"avg_deep_score"`
}
