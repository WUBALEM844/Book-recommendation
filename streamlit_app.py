import streamlit as pd
import streamlit as st
from app import BookRecommender
import os

# Set premium page configuration
st.set_page_config(
    page_title="Smart Book Recommender",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global Theme CSS Injection (Supports dynamic Light/Dark switching)
def inject_theme(theme_mode):
    if theme_mode == "Dark Space 🌙":
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: #E0E0E0; }
            .sidebar .sidebar-content { background-color: #161A24; }
            div.stButton > button:first-child {
                background-color: #4A90E2; color: white; border-radius: 8px; border: none;
            }
            .book-card {
                background-color: #1F2633; border-radius: 10px; padding: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D3748;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #F8F9FA; color: #2D3748; }
            .sidebar .sidebar-content { background-color: #FFFFFF; }
            div.stButton > button:first-child {
                background-color: #107C41; color: white; border-radius: 8px; border: none;
            }
            .book-card {
                background-color: #FFFFFF; border-radius: 10px; padding: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; border: 1px solid #E2E8F0;
            }
            </style>
        """, unsafe_allow_html=True)

# Hide native Streamlit UI elements for professional look
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Initialize Backend Recommender Engine
@st.cache_resource
def load_engine():
    recommender = BookRecommender()
    recommender.run_pipeline()
    return recommender

try:
    engine = load_engine()
except Exception as e:
    st.error(f"Error loading AI Engine: {e}")
    st.stop()

# Sidebar Layout (Configuration Controls)
st.sidebar.title("🎮 Control Panel")
st.sidebar.markdown("---")

theme = st.sidebar.selectbox("🎨 App Interface Theme", ["Light Elegance ☀️", "Dark Space 🌙"])
inject_theme(theme)

mode = st.sidebar.radio("🔄 Operational Mode", ["Simulate Existing User", "Dynamic New User Simulation"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** You can search for global titles or local masterpieces like *Fiker Eske Mekabir* or *Yene Mastawosha*.")

# Main Application Dashboard
st.title("📚 Smart Book Recommendation System")
st.subheader("Next-Generation Literary Discovery Engine powered by Cosine Similarity")
st.markdown("---")

if mode == "Simulate Existing User":
    st.header("👤 Existing User Profile Simulation")
    user_id = st.number_input("Enter target User ID from dataset:", min_value=1, value=276729, step=1)
    
    if st.button("Generate Personalized Recommendations"):
        with st.spinner("Computing vector spaces via Cosine Similarity..."):
            recommendations = engine.recommend_books(user_id=user_id)
            
            if recommendations:
                st.success(f"Top 5 book recommendations calculated for User {user_id}:")
                cols = st.columns(5)
                for idx, book in enumerate(recommendations[:5]):
                    with cols[idx]:
                        st.markdown(f"""
                            <div class="book-card">
                                <h4>📖 {book['title']}</h4>
                                <p><b>Author:</b> {book['author']}</p>
                                <p><b>Year:</b> {book['year']}</p>
                                <p><small><b>ISBN:</b> {book['isbn']}</small></p>
                            </div>
                        """, unsafe_allow_html=True)
                        # Open Library Live Redirection
                        url = f"https://openlibrary.org/search?q={book['isbn']}"
                        st.link_button("🌐 Read on Open Library", url, use_container_width=True)
            else:
                st.warning("No dynamic correlation found for this profile. Try another ID.")

else:
    st.header("✨ Live New User Profile Creator")
    st.markdown("Build a temporary profile in real-time to test the AI engine's dynamic adaptation.")
    
    # Session state initialization for real-time interaction
    if "custom_ratings" not in st.session_state:
        st.session_state.custom_ratings = {}
        
    search_query = st.text_input("🔍 Search and rate books to train your profile:")
    
    if search_query:
        # Filter books based on search query
        all_books = engine.books_df
        results = all_books[all_books['Book-Title'].str.contains(search_query, case=False, na=False)].head(5)
        
        if not results.empty:
            st.markdown("### Match Results found:")
            for _, row in results.iterrows():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{row['Book-Title']}** by {row['Book-Author']} ({row['Year-Of-Publication']})")
                with col2:
                    # Interactive Slider for explicit feedback
                    rating = st.slider("Score (1-10)", 1, 10, 8, key=f"slide_{row['ISBN']}")
                    if st.button("Add to Profile", key=f"add_{row['ISBN']}"):
                        st.session_state.custom_ratings[row['ISBN']] = rating
                        st.toast(f"Added {row['Book-Title']} with score {rating}!")
        else:
            st.error("No books match your query. Try searching 'Fiker', 'Yene', or 'Harry Potter'.")

    # Display current local training profile
    if st.session_state.custom_ratings:
        st.markdown("---")
        st.subheader("📊 Your Active Profile Parameters")
        for isbn, score in st.session_state.custom_ratings.items():
            b_info = engine.books_df[engine.books_df['ISBN'] == isbn].iloc[0]
            st.caption(f"⭐ **Score {score}/10** — {b_info['Book-Title']} ({b_info['Book-Author']})")
            
        if st.button("Compute Real-Time Recommendations"):
            with st.spinner("Evaluating multi-dimensional distance metrics..."):
                # Compute suggestions for the new dynamic profile
                recommendations = engine.recommend_for_new_user(st.session_state.custom_ratings)
                
                if recommendations:
                    st.success("AI Engine successfully synthesized your recommendations:")
                    cols = st.columns(5)
                    for idx, book in enumerate(recommendations[:5]):
                        with cols[idx]:
                            st.markdown(f"""
                                <div class="book-card">
                                    <h4>📖 {book['title']}</h4>
                                    <p><b>Author:</b> {book['author']}</p>
                                    <p><b>Year:</b> {book['year']}</p>
                                    <p><small><b>ISBN:</b> {book['isbn']}</small></p>
                                </div>
                            """, unsafe_allow_html=True)
                            url = f"https://openlibrary.org/search?q={book['isbn']}"
                            st.link_button("🌐 Read Book", url, use_container_width=True)
                else:
                    st.info("Add more diverse scores to ignite the matrix calculation.")