package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/cors"
	"github.com/joho/godotenv"
)

type Server struct {
	db     *Database
	router *chi.Mux
}

func NewServer(db *Database) *Server {
	s := &Server{
		db:     db,
		router: chi.NewRouter(),
	}

	// Middleware
	s.router.Use(middleware.Logger)
	s.router.Use(middleware.Recoverer)
	s.router.Use(cors.Handler(cors.Options{
		AllowedOrigins:   []string{"http://localhost:*", "http://127.0.0.1:*"},
		AllowedMethods:   []string{"GET", "POST", "PUT", "DELETE", "OPTIONS"},
		AllowedHeaders:   []string{"Accept", "Authorization", "Content-Type"},
		ExposedHeaders:   []string{"Link"},
		AllowCredentials: true,
		MaxAge:           300,
	}))

	// Routes
	s.router.Get("/api/articles", s.handleGetArticles)
	s.router.Get("/api/articles/{id}", s.handleGetArticle)
	s.router.Post("/api/feedback", s.handlePostFeedback)
	s.router.Get("/api/stats", s.handleGetStats)

	return s
}

func (s *Server) handleGetArticles(w http.ResponseWriter, r *http.Request) {
	// Parse query parameters
	limit, _ := strconv.Atoi(r.URL.Query().Get("limit"))
	if limit == 0 {
		limit = 20
	}
	if limit > 100 {
		limit = 100
	}

	offset, _ := strconv.Atoi(r.URL.Query().Get("offset"))
	
	minFacts, _ := strconv.ParseFloat(r.URL.Query().Get("min_facts"), 64)
	minCalm, _ := strconv.ParseFloat(r.URL.Query().Get("min_calm"), 64)
	minDeep, _ := strconv.ParseFloat(r.URL.Query().Get("min_deep"), 64)

	// Fetch articles
	articles, total, err := s.db.GetArticles(r.Context(), limit, offset, minFacts, minCalm, minDeep)
	if err != nil {
		log.Printf("Error fetching articles: %v", err)
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Return response
	response := ArticlesResponse{
		Articles: articles,
		Total:    total,
		Limit:    limit,
		Offset:   offset,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

func (s *Server) handleGetArticle(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")

	article, err := s.db.GetArticleByID(r.Context(), id)
	if err != nil {
		http.Error(w, "Article not found", http.StatusNotFound)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(article)
}

func (s *Server) handlePostFeedback(w http.ResponseWriter, r *http.Request) {
	var feedback FeedbackRequest
	if err := json.NewDecoder(r.Body).Decode(&feedback); err != nil {
		http.Error(w, "Invalid request body", http.StatusBadRequest)
		return
	}

	// Validate feedback
	if feedback.ArticleID == "" || feedback.Axis == "" {
		http.Error(w, "Missing required fields", http.StatusBadRequest)
		return
	}

	if feedback.UserScore < 0 || feedback.UserScore > 2 {
		http.Error(w, "user_score must be 0, 1, or 2", http.StatusBadRequest)
		return
	}

	// Save feedback
	if err := s.db.SaveFeedback(r.Context(), feedback); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(map[string]string{"status": "success"})
}

func (s *Server) handleGetStats(w http.ResponseWriter, r *http.Request) {
	stats, err := s.db.GetStats(r.Context())
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(stats)
}

func main() {
	// Load environment variables
	if err := godotenv.Load("../seithi-infra/.env"); err != nil {
		log.Println("No .env file found, using environment variables")
	}

	// If not set, use defaults for local development
	if os.Getenv("POSTGRES_HOST") == "" || os.Getenv("POSTGRES_HOST") == "postgres" {
		os.Setenv("POSTGRES_HOST", "localhost")
	}
	if os.Getenv("POSTGRES_PORT") == "" || os.Getenv("POSTGRES_PORT") == "5432" {
		os.Setenv("POSTGRES_PORT", "5433")
	}
	if os.Getenv("POSTGRES_USER") == "" {
		os.Setenv("POSTGRES_USER", "admin")
	}
	if os.Getenv("POSTGRES_PASSWORD") == "" {
		os.Setenv("POSTGRES_PASSWORD", "123456")
	}
	if os.Getenv("POSTGRES_DB") == "" {
		os.Setenv("POSTGRES_DB", "seithi")
	}

	// Initialize database
	db, err := NewDatabase()
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer db.Close()

	log.Println("Connected to database successfully")

	// Create server
	server := NewServer(db)

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s...", port)
	if err := http.ListenAndServe(":"+port, server.router); err != nil {
		log.Fatal("Server failed to start:", err)
	}
}
