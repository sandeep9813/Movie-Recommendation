import requests
import streamlit as st
import os

# =============================
# CONFIG
# =============================
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")
TMDB_IMG = "https://image.tmdb.org/t/p/w500"

st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")

# =============================
# CSS (Netflix Style)
# =============================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@400;500;600&display=swap');

* { box-sizing: border-box; }

.block-container {
    max-width: 1400px;
    padding-top: 1rem;
}

.netflix-row {
    display: flex;
    overflow-x: auto;
    gap: 12px;
    padding: 10px 0 16px;
    scrollbar-width: thin;
    scrollbar-color: #e50914 #1a1a1a;
}

.netflix-row::-webkit-scrollbar { height: 4px; }
.netflix-row::-webkit-scrollbar-track { background: #1a1a1a; }
.netflix-row::-webkit-scrollbar-thumb { background: #e50914; border-radius: 4px; }

.movie-card {
    min-width: 160px;
    height: 240px;
    border-radius: 10px;
    overflow: hidden;
    position: relative;
    flex-shrink: 0;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}

.movie-card:hover {
    transform: scale(1.1);
    z-index: 10;
    box-shadow: 0 12px 30px rgba(229,9,20,0.4);
}

.movie-card img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
}

.movie-title-overlay {
    position: absolute;
    bottom: 0;
    width: 100%;
    padding: 8px 6px 6px;
    font-size: 0.78rem;
    font-family: 'DM Sans', sans-serif;
    color: white;
    background: linear-gradient(to top, rgba(0,0,0,0.9) 0%, transparent 100%);
}

.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 1.6rem;
    letter-spacing: 0.05em;
    margin-top: 24px;
    margin-bottom: 4px;
    color: #f5f5f1;
}

.no-poster {
    min-width: 160px;
    height: 240px;
    border-radius: 10px;
    background: #1e1e1e;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    color: #888;
    text-align: center;
    padding: 8px;
    flex-shrink: 0;
}

/* Sticky back button */
.sticky-back > button {
    position: fixed !important;
    top: 60px !important;
    left: 16px !important;
    z-index: 9999 !important;
    background: rgba(20,20,20,0.92) !important;
    color: #fff !important;
    border: 1px solid #e50914 !important;
    border-radius: 8px !important;
    padding: 6px 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important;
    backdrop-filter: blur(6px) !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.5) !important;
    transition: background 0.2s !important;
    cursor: pointer !important;
}

.sticky-back > button:hover {
    background: #e50914 !important;
    border-color: #e50914 !important;
}
</style>
""", unsafe_allow_html=True)


# =============================
# API HELPER
# =============================
@st.cache_data(ttl=300, show_spinner=False)
def api_get(path: str, params: dict | None = None):
    """Cached GET request to the backend API."""
    try:
        r = requests.get(f"{API_BASE}{path}", params=params, timeout=20)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ Cannot reach the API server. Is it running?")
    except requests.exceptions.Timeout:
        st.error("⚠️ API request timed out.")
    except requests.exceptions.HTTPError as e:
        st.error(f"⚠️ API error: {e.response.status_code}")
    except Exception:
        pass
    return None


# =============================
# CARD NORMALIZER
# =============================
def normalize_card(movie: dict) -> dict | None:
    """
    Accept cards from multiple API shapes and normalize to
    {tmdb_id, title, poster_url}.
    Returns None if essential data is missing.
    """
    tmdb_id = movie.get("tmdb_id") or movie.get("id")
    title = movie.get("title", "Untitled")
    poster_url = movie.get("poster_url")

    # Shape from /tmdb/search results
    if not poster_url and movie.get("poster_path"):
        poster_url = f"{TMDB_IMG}{movie['poster_path']}"

    # Nested tmdb key (from recommendation bundles)
    if not poster_url:
        tmdb = movie.get("tmdb")
        if isinstance(tmdb, dict):
            tmdb_id = tmdb_id or tmdb.get("tmdb_id")
            title = tmdb.get("title", title)
            poster_url = tmdb.get("poster_url")

    if not tmdb_id or not poster_url:
        return None

    return {"tmdb_id": tmdb_id, "title": title, "poster_url": poster_url}


# =============================
# NETFLIX ROW
# =============================
def netflix_row(section_title: str, raw_cards: list, max_cols: int = 8):
    """
    Render a row of movie poster cards using native st.image().

    Keys are built from a page-level position counter that is reset to 0
    at the very start of each Streamlit script run (see STATE BOOTSTRAP).
    This gives stable, unique keys every run without relying on tmdb_id
    or section names — which breaks when the same movie appears in 2 rows.

    st.rerun() is NOT called inside the button handler. Streamlit already
    reruns the script when any widget changes; calling rerun() a second
    time inside the handler causes the click to be lost on the first run.
    """
    cards = [c for m in raw_cards if (c := normalize_card(m))]

    if not cards:
        return

    st.markdown(f"<div class='section-title'>{section_title}</div>", unsafe_allow_html=True)

    for chunk_start in range(0, len(cards), max_cols):
        chunk = cards[chunk_start : chunk_start + max_cols]
        cols = st.columns(len(chunk))

        for col, movie in zip(cols, chunk):
            with col:
                st.image(movie["poster_url"], use_container_width=True)

                # Stable positional key — unique across all rows this run
                pos = st.session_state._btn_counter
                st.session_state._btn_counter += 1

                if st.button(movie["title"], key=f"btn_{pos}", use_container_width=True):
                    st.session_state.view = "details"
                    st.session_state.movie_id = int(movie["tmdb_id"])
                    st.query_params["movie"] = str(movie["tmdb_id"])
                    # No st.rerun() here — Streamlit reruns automatically on
                    # widget interaction; a manual rerun swallows the click.


# =============================
# STATE BOOTSTRAP
# =============================
# Reset button counter at the TOP of every script run so keys are
# positionally stable and never collide across multiple netflix_row calls.
st.session_state._btn_counter = 0

# Query params take priority (e.g. deep-link or card click)
if "movie" in st.query_params:
    st.session_state.view = "details"
    st.session_state.movie_id = int(st.query_params["movie"])
elif "view" not in st.session_state:
    st.session_state.view = "home"


# =============================
# HOME PAGE
# =============================
if st.session_state.view == "home":

    st.markdown("<h1 style='font-family:Bebas Neue,sans-serif;font-size:2.8rem;letter-spacing:0.08em;'>🎬 Movie Recommender</h1>", unsafe_allow_html=True)

    query = st.text_input("🔍 Search movies", placeholder="e.g. Inception, Parasite…")

    if query:
        with st.spinner("Searching…"):
            data = api_get("/tmdb/search", {"query": query})

        if data and data.get("results"):
            netflix_row("Search Results", data["results"][:30])
        else:
            st.info("No results found. Try a different title.")

    else:
        with st.spinner("Loading content…"):
            popular  = api_get("/home", {"category": "popular",   "limit": 20}) or []
            top      = api_get("/home", {"category": "top_rated", "limit": 20}) or []
            trending = api_get("/home", {"category": "trending",  "limit": 20}) or []

        netflix_row("🔥 Trending Now", trending)
        netflix_row("⭐ Popular",       popular)
        netflix_row("🏆 Top Rated",    top)


# =============================
# DETAILS PAGE
# =============================
elif st.session_state.view == "details":

    tmdb_id = st.session_state.movie_id

    st.markdown('<div class="sticky-back">', unsafe_allow_html=True)
    if st.button("⬅ Back to Home", key="back_btn"):
        st.session_state.view = "home"
        st.session_state.pop("movie_id", None)
        st.query_params.clear()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    with st.spinner("Loading movie details…"):
        details = api_get(f"/movie/id/{tmdb_id}")

    if not details:
        st.error("Movie not found or API unavailable.")
        st.stop()

    col1, col2 = st.columns([1, 2])

    with col1:
        poster = details.get("poster_url")
        if poster:
            # FIX: use_container_width replaces deprecated width="stretch"
            st.image(poster, use_container_width=True)
        else:
            st.markdown("<div class='no-poster'>No poster available</div>", unsafe_allow_html=True)

    with col2:
        st.subheader(details.get("title", "Unknown Title"))

        meta_parts = []
        if details.get("release_date"):
            meta_parts.append(f"📅 {details['release_date'][:4]}")
        if details.get("vote_average"):
            meta_parts.append(f"⭐ {details['vote_average']:.1f}/10")
        if details.get("runtime"):
            meta_parts.append(f"⏱ {details['runtime']} min")

        if meta_parts:
            st.caption("  ·  ".join(meta_parts))

        overview = details.get("overview", "No overview available.")
        st.write(overview)

        genres = details.get("genres", [])
        if genres:
            genre_labels = " ".join(
                f"`{g['name'] if isinstance(g, dict) else g}`" for g in genres
            )
            st.markdown(genre_labels)

    st.divider()

    # ---- Recommendations ----
    with st.spinner("Finding similar movies…"):
        bundle = api_get("/movie/search", {"query": details.get("title", "")})

    if bundle:
        tfidf_raw = bundle.get("tfidf_recommendations", [])
        genre_raw = bundle.get("genre_recommendations", [])

        # Unwrap nested tmdb keys if present
        tfidf_cards = [r.get("tmdb", r) for r in tfidf_raw if r]
        genre_cards = [r.get("tmdb", r) if isinstance(r.get("tmdb"), dict) else r for r in genre_raw if r]

        if tfidf_cards:
            netflix_row("🔎 TF-IDF Similar", tfidf_cards)
        if genre_cards:
            netflix_row("🎭 Genre Matches", genre_cards)

        if not tfidf_cards and not genre_cards:
            st.info("No similar movies found for this title.")
    else:
        st.info("Recommendation service unavailable.")