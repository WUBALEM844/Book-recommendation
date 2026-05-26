import streamlit as st
import pandas as pd
import numpy as np
from app import BookRecommender
import os

# Page Configuration
st.set_page_config(
    page_title="Smart Book Recommender",
    page_icon="📚",
    layout="wide"
)

# Custom Styling Injection
def inject_custom_style(theme_mode):
    if theme_mode == "Dark Mode 🌙":
        st.markdown("""
            <style>
            .stApp { background-color: #0E1117; color: #ECEFF1; }
            .stSelectbox, .stNumberInput, .stTextInput, .stSlider { color: #FFFFFF; }
            div.stButton > button:first-child {
                background-color: #4A90E2 !important; color: white !important; border-radius: 8px;
            }
            .book-box {
                background-color: #1F2633; border: 1px solid #2D3748;
                border-radius: 12px; padding: 20px; margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3); transition: transform 0.2s;
            }
            .book-box:hover { transform: translateY(-5px); }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            .stApp { background-color: #F8F9FA; color: #2C3E50; }
            div.stButton > button:first-child {
                background-color: #107C41 !important; color: white !important; border-radius: 8px;
            }
            .book-box {
                background-color: #FFFFFF; border: 1px solid #E2E8F0;
                border-radius: 12px; padding: 20px; margin-bottom: 20px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.05); transition: transform 0.2s;
            }
            .book-box:hover { transform: translateY(-5px); }
            </style>
        """, unsafe_allow_html=True)

# Hide Streamlit Default UI Clutter
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Load AI Engine
@st.cache_resource
def get_recommender():
    recommender = BookRecommender()
    recommender.run_pipeline()
    return recommender

try:
    recommender = get_recommender()
except Exception as e:
    st.error(f"Error loading datasets: {e}")
    st.stop()

# Sidebar Setup
st.sidebar.title("🎮 Control Panel")
st.sidebar.markdown("---")

app_theme = st.sidebar.selectbox("🎨 App Interface Theme", ["Light Mode ☀️", "Dark Mode 🌙"])
inject_custom_style(app_theme)

app_mode = st.sidebar.radio("🔄 Operational Mode", ["Simulate Existing User", "Dynamic New User Simulation"])

st.sidebar.markdown("---")
st.sidebar.info("💡 **Tip:** You can search for global titles or local masterpieces like *Fiker Eske Mekabir* or *Yene Mastawosha*.")

# Main Header
st.title("📚 Smart Book Recommendation System")
st.subheader("Next-Generation Literary Discovery Engine powered by Cosine Similarity")
st.markdown("---")

if app_mode == "Simulate Existing User":
    st.header("👤 Existing User Profile Simulation")
    target_user = st.number_input("Enter target User ID from dataset:", min_value=1, value=276729, step=1)
    
    if st.button("Generate Personalized Recommendations"):
        with st.spinner("Computing vector spaces via Cosine Similarity..."):
            try:
                recs = recommender.recommend_books(user_id=target_user, top_n=5)
                if not recs.empty:
                    st.success(f"Top 5 book recommendations calculated for User {target_user}:")
                    cols = st.columns(5)
                    for idx, (_, row) in enumerate(recs.iterrows()):
                        with cols[idx]:
                            st.markdown(f"""
                                <div class="book-box">
                                    <h4 style='margin-top:0;'>📖 {row['Book-Title']}</h4>
                                    <p style='margin-bottom:4px;'><b>Author:</b> {row['Book-Author']}</p>
                                    <p style='margin-bottom:4px;'><b>Year:</b> {row['Year-Of-Publication']}</p>
                                    <p style='font-size:12px; color:#7F8C8D;'>ISBN: {row['ISBN']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            open_library_url = f"https://openlibrary.org/search?q={row['ISBN']}"
                            st.link_button("🌐 Read Book", open_library_url, use_container_width=True)
                else:
                    st.warning("No high-correlation matches found for this user profile.")
            except Exception as e:
                st.error(f"Execution Error: {e}")

else:
    st.header("✨ Live New User Profile Creator")
    st.markdown("Build a temporary profile in real-time to test the AI engine's dynamic adaptation.")
    
    if "new_user_ratings" not in st.session_state:
        st.session_state.new_user_ratings = {}
        
    search_input = st.text_input("🔍 Search and rate books to train your profile:")
    
    if search_input:
        matches = recommender.books_df[recommender.books_df['Book-Title'].str.contains(search_input, case=False, na=False)].head(5)
        
        if not matches.empty:
            st.markdown("### Match Results found:")
            for _, row in matches.iterrows():
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"**{row['Book-Title']}** by {row['Book-Author']} ({row['Year-Of-Publication']})")
                with c2:
                    score = st.slider("Score (1-10)", 1, 10, 8, key=f"rate_{row['ISBN']}")
                    if st.button("Add to Profile", key=f"btn_{row['ISBN']}"):
                        st.session_state.new_user_ratings[row['ISBN']] = score
                        st.toast(f"Added to profile with score: {score}")
        else:
            st.error("No books match your query. Try searching 'Fiker', 'Yene', or 'Harry Potter'.")

    if st.session_state.new_user_ratings:
        st.markdown("---")
        st.subheader("📊 Your Active Profile Parameters")
        for isbn, score in st.session_state.new_user_ratings.items():
            b_data = recommender.books_df[recommender.books_df['ISBN'] == isbn].iloc[0]
            st.caption(f"⭐ **Score {score}/10** — {b_data['Book-Title']} ({b_data['Book-Author']})")
            
        if st.button("Compute Real-Time Recommendations"):
            with st.spinner("Evaluating multi-dimensional distance metrics..."):
                try:
                    user_vector = pd.DataFrame(list(st.session_state.new_user_ratings.items()), columns=['ISBN', 'Book-Rating'])
                    new_recs = recommender.recommend_for_new_user(user_vector, top_n=5)
                    
                    if not new_recs.empty:
                        st.success("AI Engine successfully synthesized your recommendations:")
                        cols = st.columns(5)
                        for idx, (_, row) in enumerate(new_recs.iterrows()):
                            with cols[idx]:
                                st.markdown(f"""
                                    <div class="book-box">
                                        <h4 style='margin-top:0;'>📖 {row['Book-Title']}</h4>
                                        <p style='margin-bottom:4px;'><b>Author:</b> {row['Book-Author']}</p>
                                        <p style='margin-bottom:4px;'><b>Year:</b> {row['Year-Of-Publication']}</p>
                                        <p style='font-size:12px; color:#7F8C8D;'>ISBN: {row['ISBN']}</p>
                                    </div>
                                """, unsafe_allow_html=True)
                                open_library_url = f"https://openlibrary.org/search?q={row['ISBN']}"
                                st.link_button("🌐 Read Book", open_library_url, use_container_width=True)
                    else:
                        st.info("Add more diverse scores to ignite the matrix calculation.")
                except Exception as e:
                    st.error(f"Computation Error: {e}")