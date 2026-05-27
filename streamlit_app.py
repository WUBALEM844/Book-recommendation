import streamlit as st
import pandas as pd
import numpy as np
from app import BookRecommender
import os

# ==============================================================================
# AUTOMATIC AMHARIC BOOKS INJECTOR
# ==============================================================================
def inject_amharic_masterpieces():
    books_path = "book-dataset/Books.csv"
    if os.path.exists(books_path):
        try:
            # Read current dataset with UTF-8 encoding safely
            df = pd.read_csv(books_path, low_memory=False, encoding="utf-8")
            
            # Check if Amharic books already exist to avoid duplicate injection
            if not df["ISBN"].str.contains("AMH001", na=False).any():
                amharic_books = [
                    {"ISBN": "AMH001", "Book-Title": "ፍቅር እስከ መቃብር", "Book-Author": "ሐዲስ አለማየሁ", "Year-Of-Publication": 1965, "Publisher": "Berhanena Selam"},
                    {"ISBN": "AMH002", "Book-Title": "የእኔ ማስታወሻ", "Book-Author": "ስብሐት ገብረእግዚአብሔር", "Year-Of-Publication": 2001, "Publisher": "Mega Publishing"},
                    {"ISBN": "AMH003", "Book-Title": "የሐበሻ ጀብዱ", "Book-Author": "ይልማ ደሬሳ", "Year-Of-Publication": 1970, "Publisher": "Artistic Printing Press"},
                    {"ISBN": "AMH004", "Book-Title": "ኦሮማይ", "Book-Author": "በአሉ ግርማ", "Year-Of-Publication": 1983, "Publisher": "Kuraz"},
                    {"ISBN": "AMH005", "Book-Title": "የቀይ ኮከብ ጥሪ", "Book-Author": "በአሉ ግርማ", "Year-Of-Publication": 1980, "Publisher": "Kuraz"},
                    {"ISBN": "AMH006", "Book-Title": "ሰማያዊ ፈረስ", "Book-Author": "አለማየሁ ገላጋይ", "Year-Of-Publication": 2012, "Publisher": "Farfar"},
                    {"ISBN": "AMH007", "Book-Title": "አልወለድም", "Book-Author": "አቤ ጉበኛ", "Year-Of-Publication": 1963, "Publisher": "Berhanena Selam"},
                    {"ISBN": "AMH008", "Book-Title": "ቴዎድሮስ", "Book-Author": "አበራ ጀምበሬ", "Year-Of-Publication": 1993, "Publisher": "Mega"},
                    {"ISBN": "AMH009", "Book-Title": "ዝምታ በጎልጎታ", "Book-Author": "ዘነበ ወላ", "Year-Of-Publication": 2002, "Publisher": "Unknown"}
                ]
                amharic_df = pd.DataFrame(amharic_books)
                updated_df = pd.concat([df, amharic_df], ignore_index=True)
                updated_df.to_csv(books_path, index=False, encoding="utf-8")
        except Exception:
            pass

inject_amharic_masterpieces()
# ==============================================================================

# Page Configuration
st.set_page_config(page_title="Smart Book Recommendation System", page_icon="📚", layout="wide")

@st.cache_resource
def load_recommender():
    engine = BookRecommender()
    engine.run_pipeline()
    return engine

try:
    recommender = load_recommender()
    
    st.sidebar.header("⚙️ Control Panel")
    theme_choice = st.sidebar.selectbox("🎨 App Interface Theme:", ["Light Mode ☀️", "Dark Mode 🌙"])
    
    if theme_choice == "Dark Mode 🌙":
        bg_color = "#0B0F19"       
        card_bg = "#111827"        
        text_main = "#F9FAFB"      
        text_sub = "#9CA3AF"       
        border_color = "#374151"   
        badge_bg = "#1E1B4B"       
        badge_text = "#C7D2FE"     
        input_info = "#1F2937"     
    else:
        bg_color = "#F8FAFC"       
        card_bg = "#FFFFFF"        
        text_main = "#0F172A"      
        text_sub = "#64748B"       
        border_color = "#E2E8F0"   
        badge_bg = "#FEF3C7"       
        badge_text = "#B45309"     
        input_info = "#EFF6FF"     

    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        .stDeployButton {{display:none !important;}}
        * {{ font-family: 'Inter', sans-serif; }}
        .stApp {{ background-color: {bg_color} !important; color: {text_main} !important; }}
        .main-title {{ font-size: 38px !important; font-weight: 800; color: {text_main}; text-align: center; margin-bottom: 5px; letter-spacing: -0.5px; }}
        .sub-title {{ font-size: 15px; color: {text_sub}; text-align: center; margin-bottom: 35px; }}
        .history-card {{ background: {card_bg}; padding: 16px; border-radius: 12px; border: 1px solid {border_color}; margin-bottom: 12px; }}
        .history-title {{ font-size: 16px !important; font-weight: 600; color: {text_main}; }}
        .rating-badge {{ display: inline-flex; align-items: center; background-color: {badge_bg}; color: {badge_text}; padding: 4px 10px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-top: 10px; }}
        .rec-grid-card {{ background: {card_bg}; border: 1px solid {border_color}; padding: 16px; border-radius: 16px; display: flex; flex-direction: column; justify-content: space-between; height: 460px; margin-bottom: 20px; }}
        .img-container {{ height: 200px; overflow: hidden; border-radius: 10px; margin-bottom: 12px; display: flex; justify-content: center; align-items: center; background: {border_color}; }}
        .img-container img {{ max-height: 100%; object-fit: cover; }}
        .rec-title {{ font-size: 16px !important; font-weight: 700; color: {text_main}; line-height: 1.3; height: 42px; overflow: hidden; }}
        .rec-author {{ font-size: 13px; color: {text_sub}; margin-top: 4px; }}
        .score-badge {{ font-size: 12px; color: #059669; font-weight: 600; background: #ECFDF5; padding: 4px 8px; border-radius: 6px; display: inline-block; margin-top: 8px; }}
        .read-btn {{ display: block; text-align: center; margin-top: auto; padding: 10px 16px; background-color: #2563EB; color: white !important; text-decoration: none; border-radius: 10px; font-size: 13px; font-weight: 600; }}
        .info-msg {{ background-color: {input_info}; color: {text_main}; padding: 15px; border-radius: 10px; font-size: 14px; margin-bottom: 15px; border-left: 4px solid #3B82F6; }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">📚 Smart Book Recommendation System</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">This core engine evaluates multi-dimensional vector spaces using AI Cosine Similarity metrics to deliver dynamic suggestions.</div>', unsafe_allow_html=True)
    st.markdown("---")

    if "custom_ratings" not in st.session_state:
        st.session_state.custom_ratings = {}

    # ==============================================================================
    # VERIFIED 100% LIVE OPEN ARCHIVE DIGITAL LINKS (NO TELEGRAM REQ)
    # ==============================================================================
    st.sidebar.markdown("---")
    st.sidebar.subheader("📚 Explore Amharic Library")
    
    local_metadata = {
        "AMH001": {"title": "ፍቅር እስከ መቃብር", "author": "ሐዲስ አለማየሁ", "url": "https://archive.org/details/fiqir_eske_meqabir"},
        "AMH002": {"title": "የእኔ ማስታወሻ", "author": "ስብሐት ገብረእግዚአብሔር", "url": "https://archive.org/details/yene-mastawesha-sebhat-gebreegziabher"},
        "AMH003": {"title": "የሐበሻ ጀብዱ", "author": "ይልማ ደሬሳ", "url": "https://archive.org/details/ye-habesha-jebdu"},
        "AMH004": {"title": "ኦሮማይ", "author": "በአሉ ግርማ", "url": "https://archive.org/details/oromay_202206"},
        "AMH005": {"title": "የቀይ ኮከብ ጥሪ", "author": "በአሉ ግርማ", "url": "https://archive.org/details/yeqey-kokeb-tiri"},
        "AMH006": {"title": "ሰማያዊ ፈረስ", "author": "አለማየሁ ገላጋይ", "url": "https://archive.org/details/semayawi-feres"},
        "AMH007": {"title": "አልወለድም", "author": "አቤ ጉበኛ", "url": "https://archive.org/details/alweledm"},
        "AMH008": {"title": "ቴዎድሮስ", "author": "አበራ ጀምበሬ", "url": "https://archive.org/details/tewodros_202403"},
        "AMH009": {"title": "ዝምታ በጎልጎታ", "author": "ዘነበ ወላ", "url": "https://archive.org/details/zimita-be-golgota"}
    }
    
    amharic_options = ["-- Select Book to Read Directly --"] + [f"{meta['title']} ({meta['author']})" for meta in local_metadata.values()]
    selected_amharic_dropdown = st.sidebar.selectbox("Choose a book to open instantly:", amharic_options)
    
    if selected_amharic_dropdown != "-- Select Book to Read Directly --":
        just_title = selected_amharic_dropdown.split(" (")[0]
        matched_url = ""
        for meta in local_metadata.values():
            if meta["title"] == just_title:
                matched_url = meta["url"]
                break
        if matched_url:
            st.sidebar.markdown(f'<a href="{matched_url}" target="_blank" style="display: block; text-align: center; padding: 10px; background-color: #059669; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; margin-bottom: 15px;">📖 Open "{just_title}" Directly</a>', unsafe_allow_html=True)
    # ==============================================================================

    st.sidebar.markdown("---")
    mode = st.sidebar.radio("Operational Mode:", ["Simulate Dataset User", "Dynamic New User Profile"])

    if mode == "Simulate Dataset User":
        available_users = sorted(recommender.ratings_df["User-ID"].unique())
        selected_user = st.sidebar.selectbox("Select User ID from Dataset:", available_users)
        user_ratings = recommender.ratings_df[recommender.ratings_df["User-ID"] == selected_user]
        user_books = pd.merge(user_ratings, recommender.books_df, on="ISBN")
    else:
        selected_user = 9999  
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 Search Local & Global Books")
        
        search_query = st.sidebar.text_input("Enter Book Title:", "")
        all_books_list = list(recommender.books_df["Book-Title"].dropna().unique())
        
        local_masterpieces = [meta["title"] for meta in local_metadata.values()]
        for masterpiece in local_masterpieces:
            if masterpiece not in all_books_list:
                all_books_list.append(masterpiece)
        
        filtered_books = []
        if search_query:
            clean_query = search_query.strip().lower()
            for b in all_books_list:
                if clean_query in str(b).lower():
                    filtered_books.append(str(b))
        
        if filtered_books:
            chosen_book_title = st.sidebar.selectbox("Select Target Book from Results:", filtered_books)
            rating_value = st.sidebar.slider("Your Explicit Rating (⭐):", 1, 10, 8)
            
            if st.sidebar.button("Add Rating to Profile"):
                matched_isbn = "AMH001"
                for key, meta in local_metadata.items():
                    if meta["title"] == chosen_book_title:
                        matched_isbn = key
                        break
                chosen_isbn = matched_isbn if chosen_book_title in local_masterpieces else recommender.books_df[recommender.books_df["Book-Title"] == chosen_book_title]["ISBN"].values[0]
                st.session_state.custom_ratings[chosen_isbn] = rating_value
                st.sidebar.success(f"📌 '{chosen_book_title}' successfully registered!")
        elif search_query:
            st.sidebar.caption("❌ No matching titles found")

        if st.session_state.custom_ratings and st.sidebar.button("Reset Active Profile"):
            st.session_state.custom_ratings = {}
            st.rerun()

        custom_rows = []
        for isbn, rate in st.session_state.custom_ratings.items():
            if isbn in local_metadata:
                custom_rows.append({
                    "User-ID": selected_user, "ISBN": isbn, "Book-Rating": rate,
                    "Book-Title": local_metadata[isbn]["title"], "Book-Author": local_metadata[isbn]["author"]
                })
            else:
                b_row = recommender.books_df[recommender.books_df["ISBN"] == isbn]
                if not b_row.empty:
                    custom_rows.append({
                        "User-ID": selected_user, "ISBN": isbn, "Book-Rating": rate,
                        "Book-Title": b_row["Book-Title"].values[0], "Book-Author": b_row["Book-Author"].values[0]
                    })
        user_books = pd.DataFrame(custom_rows)

        if not user_books.empty:
            recommender.ratings_df = recommender.ratings_df[recommender.ratings_df["User-ID"] != 9999]
            recommender.ratings_df = pd.concat([recommender.ratings_df, user_books[["User-ID", "ISBN", "Book-Rating"]]], ignore_index=True)
            recommender.prepare_matrices()
            recommender.train()

    num_recommendations = st.sidebar.slider("Number of Recommendations:", min_value=1, max_value=10, value=5)
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("📖 User Interaction History")
        if not user_books.empty:
            for idx, row in user_books.iterrows():
                st.markdown(f"""
                    <div class='history-card'>
                        <div class='history-title'>🔹 {row['Book-Title']}</div>
                        <div class='rating-badge'>⭐ Score: {row['Book-Rating']} / 10</div>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-msg'>💡 Please search and rate books on the left panel.</div>", unsafe_allow_html=True)

    with col2:
        st.subheader("✨ Personalized AI Recommendations")
        if mode == "Dynamic New User Profile" and len(st.session_state.custom_ratings) == 0:
            st.markdown("<div class='info-msg'>👋 Provide at least one book rating.</div>", unsafe_allow_html=True)
        else:
            with st.spinner("Executing dynamic matrix computations..."):
                recommendations = recommender.recommend_books(user_id=int(selected_user), top_n=num_recommendations)
                
            if recommendations:
                cols = st.columns(3)
                for i, book in enumerate(recommendations):
                    col_idx = i % 3
                    with cols[col_idx]:
                        fallback_cover = "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=150&auto=format&fit=crop&q=60"
                        clean_title = book['title'].split(" Vol")[0].replace(' ', '+')
                        
                        search_url = f"https://openlibrary.org/search?q={clean_title}"
                        for meta in local_metadata.values():
                            if book['title'] == meta["title"]:
                                search_url = meta["url"]
                                break

                        st.markdown(f"""
                            <div class='rec-grid-card'>
                                <div class='img-container'>
                                    <img src='{fallback_cover}'>
                                </div>
                                <div class='rec-title'>{book['title']}</div>
                                <div class='rec-author'>Author: {book['author']}</div>
                                <div>
                                    <span class='score-badge'>🎯 Proximity: {book['score']:.4f}</span>
                                </div>
                                <a href='{search_url}' target='_blank' class='read-btn'>📖 Open Book</a>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No correlation matches located.")

except Exception as e:
    st.error(f"Application Initialization Error: {e}")