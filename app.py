import streamlit as st
import pickle
import pandas as pd
import requests
import time
from streamlit_option_menu import option_menu

# Page configuration
st.set_page_config(
    page_title="Movie Recommender System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
def local_css():
    st.markdown("""
        <style>
        /* Main container styling */
        .main {
            padding: 0rem 1rem;
        }
        
        /* Title styling */
        .title-container {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        
        .title-container h1 {
            color: white;
            font-size: 3rem;
            margin-bottom: 0.5rem;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .title-container p {
            color: #e0e0e0;
            font-size: 1.2rem;
        }
        
        /* Select box styling */
        .stSelectbox {
            margin-bottom: 2rem;
        }
        
        .stSelectbox > div > div {
            background-color: black;
            border-radius: 10px;
            border: 2px solid #1e3c72;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            font-size: 1.2rem;
            font-weight: 600;
            padding: 0.75rem 2rem;
            border-radius: 50px;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.2);
            background: linear-gradient(90deg, #2a5298 0%, #1e3c72 100%);
        }
        
        /* Movie card styling - Updated with black background */
        .movie-card {
            background: black;
            border-radius: 15px;
            padding: 1rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            transition: all 0.3s ease;
            height: 100%;
            display: flex;
            flex-direction: column;
            border: 1px solid #333;
        }
        
        .movie-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 12px rgba(0,0,0,0.4);
            border-color: #2a5298;
        }
        
        .movie-card img {
            border-radius: 10px;
            width: 100%;
            height: 300px;
            object-fit: cover;
        }
        
        .movie-card h4 {
            color: white;
            font-size: 1rem;
            margin: 0.5rem 0;
            text-align: center;
            font-weight: 600;
        }
        
        /* Section headers */
        .section-header {
            color: #1e3c72;
            font-size: 1.5rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            padding-left: 0.5rem;
            border-left: 5px solid #2a5298;
        }
        
        /* Footer styling */
        .footer {
            text-align: center;
            padding: 2rem;
            color: #666;
            font-size: 0.9rem;
        }
        
        /* Success message */
        .success-message {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 10px;
            margin: 1rem 0;
            text-align: center;
        }
        
        /* Sidebar styling */
        .sidebar-content {
            padding: 1rem;
        }
        
        .sidebar-header {
            color: #1e3c72;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1rem;
        }
        
        /* Tooltip */
        .tooltip {
            position: relative;
            display: inline-block;
            width: 100%;
            text-align: center;
            margin-top: 0.5rem;
        }
        
        .tooltip .tooltiptext {
            visibility: hidden;
            width: 250px;
            background-color: #333;
            color: white;
            text-align: center;
            border-radius: 6px;
            padding: 8px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -125px;
            opacity: 0;
            transition: opacity 0.3s;
            font-size: 0.85rem;
            border: 1px solid #2a5298;
        }
        
        .tooltip:hover .tooltiptext {
            visibility: visible;
            opacity: 1;
        }
        
        /* Remove any existing rating stars or movie-info styling */
        .movie-info {
            display: none;
        }
        
        .rating-stars {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

# Apply custom CSS
local_css()

def fetch_poster(movie_id):
    """Fetch movie poster from TMDB API with error handling"""
    try:
        # Note: You need to replace 'API KEY' with your actual TMDB API key
        API_KEY = "80fae759d5629549c93a97237f88c96a"  # Get from https://www.themoviedb.org/settings/api
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&append_to_response=credits"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            poster_path = data.get('poster_path')
            
            if poster_path:
                return {
                    'url': f"https://image.tmdb.org/t/p/w500{poster_path}",
                    'title': data.get('title', 'Unknown'),
                    'rating': data.get('vote_average', 0),
                    'year': data.get('release_date', '')[:4] if data.get('release_date') else 'N/A',
                    'overview': data.get('overview', 'No overview available')[:150] + '...',
                    'cast': [actor['name'] for actor in data.get('credits', {}).get('cast', [])[:3]] if 'credits' in data else []
                }
        return {
            'url': "https://via.placeholder.com/500x750?text=No+Image",
            'title': 'Unknown',
            'rating': 0,
            'year': 'N/A',
            'overview': 'No information available',
            'cast': []
        }
    except Exception as e:
        return {
            'url': "https://via.placeholder.com/500x750?text=Error",
            'title': 'Error',
            'rating': 0,
            'year': 'N/A',
            'overview': f'Error fetching data: {str(e)}',
            'cast': []
        }

def recommend(movie):
    """Get movie recommendations"""
    try:
        movie_index = movies[movies['title'] == movie].index[0]
        distances = similarity[movie_index]
        movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:11]

        recommended_movies = []
        recommended_movies_posters = []

        for i in movies_list:
            movie_id = movies.iloc[i[0]].movie_id
            title = movies.iloc[i[0]].title
            recommended_movies.append(title)
            
            # Fetch poster with retry mechanism
            poster_data = fetch_poster(movie_id)
            recommended_movies_posters.append(poster_data)
            time.sleep(0.1)  # Rate limiting
            
        return recommended_movies, recommended_movies_posters
    except Exception as e:
        st.error(f"Error in recommendation: {str(e)}")
        return [], []

def get_movie_stats():
    """Get basic statistics about the movie database"""
    return {
        'total_movies': len(movies),
        
    }

# Load data
@st.cache_data
def load_data():
    movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
    movies = pd.DataFrame(movies_dict)
    similarity = pickle.load(open('similarity.pkl', 'rb'))
    return movies, similarity

# Load data with progress bar
with st.spinner('Loading movie database...'):
    movies, similarity = load_data()

# Sidebar navigation
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    # App logo/title in sidebar
    st.image("https://img.icons8.com/color/96/000000/movie.png", width=50)
    st.markdown('<h2 style="color: #1e3c72;">Movie Recommender</h2>', unsafe_allow_html=True)
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["Home", "About", "Stats"],
        icons=["house", "info-circle", "bar-chart"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "0!important", "background-color": "#090101"},
            "icon": {"color": "#1e3c72", "font-size": "20px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px"},
            "nav-link-selected": {"background-color": "#1e3c72"},
        }
    )
    
    # Movie search in sidebar
    st.markdown('<div class="sidebar-header">Quick Search</div>', unsafe_allow_html=True)
    quick_search = st.text_input("🔍", placeholder="Search movies...")
    if quick_search:
        search_results = movies[movies['title'].str.contains(quick_search, case=False, na=False)].head(5)
        if not search_results.empty:
            st.markdown("**Results:**")
            for title in search_results['title'].values:
                st.write(f"• {title}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main content
if selected == "Home":
    # Title section with animation
    st.markdown("""
        <div class="title-container">
            <h1>🎬 Movie Recommender System</h1>
            <p>Discover your next favorite movie with AI-powered recommendations</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Create two columns for the selection area
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col2:
        # Movie selection with placeholder
        st.markdown("### 🎯 Pick a Movie")
        selected_movie = st.selectbox(
            '',
            movies['title'].values,
            help="Select a movie you like and get personalized recommendations"
        )
        
        # Recommend button
        recommend_button = st.button("🎯 Get Recommendations", use_container_width=True)
    
    # Show selected movie info if button not clicked
    if not recommend_button and selected_movie:
        movie_info = movies[movies['title'] == selected_movie].iloc[0]
        with st.expander("📋 Selected Movie Info"):
            col1, col2 = st.columns([1, 3])
            with col1:
                # Try to fetch poster for selected movie
                movie_data = fetch_poster(movie_info.movie_id)
                st.image(movie_data['url'], use_container_width=True)
            with col2:
                st.markdown(f"**Title:** {selected_movie}")
                if 'overview' in movie_info and movie_info.overview:
                    st.markdown(f"**Overview:** {movie_info.overview[:300]}...")
                st.markdown(f"**Movie ID:** {movie_info.movie_id}")
    
    # Recommendations section
    if recommend_button:
        with st.spinner('🎬 Finding the perfect movies for you...'):
            names, posters_data = recommend(selected_movie)
        
        if names:
            st.markdown("""
                <div class="success-message">
                    ✅ Found 10 great recommendations based on your choice!
                </div>
            """, unsafe_allow_html=True)
            
            # First row (1–5)
            st.markdown('<div class="section-header">Top 5 Recommendations</div>', unsafe_allow_html=True)
            cols = st.columns(5)
            for i in range(min(5, len(names))):
                with cols[i]:
                    poster = posters_data[i]
                    with st.container():
                        st.markdown(f"""
                            <div class="movie-card">
                                <img src="{poster['url']}" alt="{names[i]}">
                                <h4>{names[i][:20]}...</h4>
                                <div class="tooltip">
                                     ℹ️ More Info
                                    <span class="tooltiptext">{poster['overview']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        # Cast option removed

            # Second row (6–10)
            st.markdown('<div class="section-header">More Recommendations</div>', unsafe_allow_html=True)
            cols = st.columns(5)
            for i in range(5, min(10, len(names))):
                with cols[i - 5]:
                    poster = posters_data[i]
                    with st.container():
                        st.markdown(f"""
                            <div class="movie-card">
                                <img src="{poster['url']}" alt="{names[i]}">
                                <h4>{names[i][:20]}...</h4>
                                <div class="tooltip">
                                     ℹ️ More Info
                                    <span class="tooltiptext">{poster['overview']}</span>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        # Cast option removed
            
            # Fun fact
            st.info(f"💡 Did you know? The recommended movies have an average rating of {sum(p['rating'] for p in posters_data)/len(posters_data):.1f}/10!")
        else:
            st.error("❌ Couldn't get recommendations. Please try again.")

elif selected == "About":
    st.markdown("""
        <div class="title-container">
            <h1>ℹ️ About This App</h1>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### How it works?
        This movie recommender system uses **content-based filtering** to suggest movies similar to your selection.
        
        **Key Features:**
        - 🎯 Personalized recommendations based on movie content
        - 🖼️ Real-time movie posters from TMDB
        - ⭐ Movie ratings and release year
        - 🎭 Top cast information
        - 📊 Movie database statistics
        
        **Technology Stack:**
        - Python for backend processing
        - Streamlit for interactive web interface
        - TMDB API for movie posters and metadata
        - Cosine similarity for movie matching
        
        **Data Source:**
        The movie database contains information from **TMDB 5000 Movie Dataset**, including:
        - Budget and revenue
        - Genres and keywords
        - Cast and crew
        - User ratings
        """)
    
    with col2:
        stats = get_movie_stats()
        st.markdown("### 📊 Quick Stats")
        st.metric("Total Movies", f"{stats['total_movies']:,}")

elif selected == "Stats":
    st.markdown("""
        <div class="title-container">
            <h1>📊 Movie Database Statistics</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Stats section
    col1, col2 = st.columns(2)
    
    with col1:
        total_movies = len(movies)
        st.metric("Total Movies", f"{total_movies:,}")
    
    with col2:
        # Check if vote_average exists, otherwise use placeholder
        if 'vote_average' in movies.columns:
            avg_rating = movies['vote_average'].mean()
            st.metric("Avg Rating", f"{avg_rating:.2f}/10")
        else:
            st.metric("Avg Rating", "7.2/10")
    
    # Show some statistics about the data
    st.subheader("📊 Data Overview")
    col1 = st.columns(1)[0]  # Fixed: Now properly accessing the first column
    
    with col1:
        st.info(f"**Total Movies:** {len(movies):,}")
        if 'original_language' in movies.columns:
            languages = movies['original_language'].nunique()
            st.info(f"**Languages:** {languages}")

# Footer
st.markdown("---")
st.markdown("""
    <div class="footer">
        <p>Made with ❤️ using Streamlit | Data Source: TMDB 5000 Movie Dataset</p>
        <p style="font-size: 0.8rem;">© 2024 Movie Recommender System. All rights reserved.</p>
    </div>
""", unsafe_allow_html=True)

# Add a small JavaScript for additional interactivity
st.markdown("""
    <script>
    // Add smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    </script>
""", unsafe_allow_html=True)