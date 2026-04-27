🎬 Movie Recommendation System

A full-stack Movie Recommendation Web App built using FastAPI (backend) and Streamlit (frontend).
It recommends movies using TF-IDF based similarity + genre-based filtering + TMDB API integration and provides a Netflix-style UI for smooth browsing.

🚀 Live Features
🔍 Movie search with autocomplete (TMDB API)
🎬 Netflix-style UI with horizontal scrolling rows
🤖 TF-IDF based recommendation engine
🎭 Genre-based recommendations
📄 Detailed movie information page
🖼️ High-quality movie posters from TMDB
⚡ Fast API backend with structured endpoints
🧠 Recommendation System

This project uses a hybrid recommendation approach:

1. TF-IDF Content-Based Filtering
Uses movie metadata (title, overview, genres)
Computes similarity using TF-IDF + cosine similarity
Finds movies similar to selected title
2. Genre-Based Filtering
Uses TMDB genre IDs
Suggests movies from the same category
3. TMDB Integration
Fetches:
Posters
Backdrops
Movie details
Trending / Popular movies




🏗️ Tech Stack
Backend
FastAPI
Pandas
NumPy
Scikit-learn (TF-IDF)
httpx (API requests)
Frontend
Streamlit
HTML/CSS (custom Netflix-style UI)
Requests
External API
TMDB API (The Movie Database)
