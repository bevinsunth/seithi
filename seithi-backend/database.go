package main

import (
	"context"
	"fmt"
	"os"

	"github.com/jackc/pgx/v5/pgxpool"
)

type Database struct {
	pool *pgxpool.Pool
}

// NewDatabase creates a new database connection pool
func NewDatabase() (*Database, error) {
	dbURL := fmt.Sprintf(
		"postgres://%s:%s@%s:%s/%s",
		os.Getenv("POSTGRES_USER"),
		os.Getenv("POSTGRES_PASSWORD"),
		os.Getenv("POSTGRES_HOST"),
		os.Getenv("POSTGRES_PORT"),
		os.Getenv("POSTGRES_DB"),
	)

	pool, err := pgxpool.New(context.Background(), dbURL)
	if err != nil {
		return nil, fmt.Errorf("unable to create connection pool: %w", err)
	}

	return &Database{pool: pool}, nil
}

// Close closes the database connection pool
func (db *Database) Close() {
	db.pool.Close()
}

// GetArticles fetches articles with optional filtering
func (db *Database) GetArticles(ctx context.Context, limit, offset int, minFacts, minCalm, minDeep float64) ([]Article, int, error) {
	query := `
		SELECT 
			id, title, url, domain, published_at,
			epistemic_opinion_score, epistemic_mixed_score, epistemic_facts_score,
			emotive_triggering_score, emotive_mixed_score, emotive_calm_score,
			density_fluff_score, density_standard_score, density_deep_score
		FROM seithi.articles
		WHERE epistemic_facts_score >= $1
		  AND emotive_calm_score >= $2
		  AND density_deep_score >= $3
		ORDER BY density_deep_score DESC, emotive_calm_score DESC, published_at DESC
		LIMIT $4 OFFSET $5
	`

	rows, err := db.pool.Query(ctx, query, minFacts, minCalm, minDeep, limit, offset)
	if err != nil {
		return nil, 0, fmt.Errorf("query failed: %w", err)
	}
	defer rows.Close()

	var articles []Article
	for rows.Next() {
		var a Article
		err := rows.Scan(
			&a.ID, &a.Title, &a.URL, &a.Domain, &a.PublishedAt,
			&a.EpistemicOpinionScore, &a.EpistemicMixedScore, &a.EpistemicFactsScore,
			&a.EmotiveTriggeringScore, &a.EmotiveMixedScore, &a.EmotiveCalmScore,
			&a.DensityFluffScore, &a.DensityStandardScore, &a.DensityDeepScore,
		)
		if err != nil {
			return nil, 0, fmt.Errorf("scan failed: %w", err)
		}
		articles = append(articles, a)
	}

	// Get total count
	var total int
	countQuery := `
		SELECT COUNT(*)
		FROM seithi.articles
		WHERE epistemic_facts_score >= $1
		  AND emotive_calm_score >= $2
		  AND density_deep_score >= $3
	`
	err = db.pool.QueryRow(ctx, countQuery, minFacts, minCalm, minDeep).Scan(&total)
	if err != nil {
		return nil, 0, fmt.Errorf("count query failed: %w", err)
	}

	return articles, total, nil
}

// GetArticleByID fetches a single article by ID
func (db *Database) GetArticleByID(ctx context.Context, id string) (*Article, error) {
	query := `
		SELECT 
			id, title, url, domain, published_at,
			epistemic_opinion_score, epistemic_mixed_score, epistemic_facts_score,
			emotive_triggering_score, emotive_mixed_score, emotive_calm_score,
			density_fluff_score, density_standard_score, density_deep_score
		FROM seithi.articles
		WHERE id = $1
	`

	var a Article
	err := db.pool.QueryRow(ctx, query, id).Scan(
		&a.ID, &a.Title, &a.URL, &a.Domain, &a.PublishedAt,
		&a.EpistemicOpinionScore, &a.EpistemicMixedScore, &a.EpistemicFactsScore,
		&a.EmotiveTriggeringScore, &a.EmotiveMixedScore, &a.EmotiveCalmScore,
		&a.DensityFluffScore, &a.DensityStandardScore, &a.DensityDeepScore,
	)
	if err != nil {
		return nil, fmt.Errorf("query failed: %w", err)
	}

	return &a, nil
}

// SaveFeedback saves user feedback to the feedback_log table
func (db *Database) SaveFeedback(ctx context.Context, feedback FeedbackRequest) error {
	query := `
		INSERT INTO seithi.feedback_log (article_id, axis, user_score, timestamp)
		VALUES ($1, $2, $3, NOW())
	`

	_, err := db.pool.Exec(ctx, query, feedback.ArticleID, feedback.Axis, feedback.UserScore)
	if err != nil {
		return fmt.Errorf("insert failed: %w", err)
	}

	return nil
}

// GetStats returns overall statistics
func (db *Database) GetStats(ctx context.Context) (*StatsResponse, error) {
	query := `
		SELECT 
			COUNT(*) as total,
			AVG(epistemic_facts_score) as avg_facts,
			AVG(emotive_calm_score) as avg_calm,
			AVG(density_deep_score) as avg_deep
		FROM seithi.articles
	`

	var stats StatsResponse
	err := db.pool.QueryRow(ctx, query).Scan(
		&stats.TotalArticles,
		&stats.AvgFactsScore,
		&stats.AvgCalmScore,
		&stats.AvgDeepScore,
	)
	if err != nil {
		return nil, fmt.Errorf("query failed: %w", err)
	}

	return &stats, nil
}
