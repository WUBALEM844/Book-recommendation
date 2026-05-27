import streamlit as st
import pandas as pd
import numpy as np
from app import BookRecommender
import os

# ==============================================================================
# DIRECT AMHARIC FULL PDF BOOKS DATABASE (EMBEDDED INTERNAL READER)
# ==============================================================================
amharic_library = {
    "AMH001": {
        "title": "ፍቅር እስከ መቃብር", 
        "author": "ሐዲስ አለማየሁ", 
        "pdf_url": "https://www.oromalibrary.com/wp-content/uploads/2021/04/Fikir-Eske-Mekabir.pdf",
        "cover": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=200"
    },
    "AMH002": {
        "title": "ኦሮማይ", 
        "author": "በአሉ ግርማ", 
        "pdf_url": "https://ia801606.us.archive.org/21/items/oromay_202206/oromay.pdf",
        "cover": "https://images.unsplash.com/photo-1506880018603-83d5b814b5a6?w=200"
    }
}

def inject_amharic_masterpieces():
    books_path = "book-dataset/Books.csv"
    if os.path.exists(books_path):
        try:
            df = pd.read_csv(books_path, low_memory=False, encoding="utf-8")
            if not df["ISBN"].str.contains("AMH001", na=False).any():
                amharic_rows = [
                    {"ISBN": k, "Book-Title": v["title"], "Book-Author": v["author"], "Year-Of-Publication": 1980, "Publisher": "Local"}
                    for k, v in amharic_library.items()
                ]
                updated_df = pd.concat([df, pd.DataFrame(amharic_rows)], ignore_index=True)
                updated_df.to_csv(books_path, index=False, encoding="utf-8")
        except Exception:
            pass

inject_amharic_masterpieces()
# ==============================================================================

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
        bg_color = "#0B0F19"; card_bg = "#111827"; text_main = "#F9FAFB"; text_sub = "#9CA3AF"; border_color = "#374151"
    else:
        bg_color = "#F8FAFC"; card_bg = "#FFFFFF"; text_main = "#0F172A"; text_sub = "#64748B"; border_color = "#E2E8F0"

    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg_color} !important; color: {text_main} !important; }}
        .rec-grid-card {{ background: {card_bg}; border: 1px solid {border_color}; padding: 16px; border-radius: 16px; display: flex; flex-direction: column; justify-content: space-between; height: 440px; margin-bottom: 20px; }}
        .img-container {{ height: 180px; overflow: hidden; border-radius: 10px; margin-bottom: 12px; display: flex; justify-content: center; align-items: center; background: {border_color}; }}
        .img-container img {{ max-height: 100%; object-fit: cover; }}
        .rec-title {{ font-size: 16px !important; font-weight: 700; color: {text_main}; height: 42px; overflow: hidden; }}
        .rec-author {{ font-size: 13px; color: {text_sub}; }}
        .score-badge {{ font-size: 12px; color: #059669; font-weight: 600; background: #ECFDF5; padding: 4px 8px; border-radius: 6px; display: inline-block; }}
        .read-btn {{ display: block; text-align: center; margin-top: auto; padding: 10px 16px; background-color: #2563EB; color: white !important; text-decoration: none; border-radius: 10px; font-size: 13px; font-weight: 600; }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<h1 style="text-align: center;">📚 Smart Book Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown("---")

    if "custom_ratings" not in st.session_state:
        st.session_state.custom_ratings = {}
    if "active_pdf_url" not in st.session_state:
        st.session_state.active_pdf_url = None
    if "active_pdf_title" not in st.session_state:
        st.session_state.active_pdf_title = None

    # THE INTERNAL PDF EMBEDDED VIEWER (OPENS AMHARIC FULL BOOK ON SCREEN!)
    if st.session_state.active_pdf_url:
        st.markdown(f"### 📖 አሁን እያነበቡት ነው፦ **{st.session_state.active_pdf_title}**")
        if st.button("❌ መጽሐፉን ዝጋ (Close Book)"):
            st.session_state.active_pdf_url = None
            st.session_state.active_pdf_title = None
            st.rerun()
            
        st.markdown(f"""
            <iframe src="{st.session_state.active_pdf_url}" width="100%" height="800px" style="border: none; border-radius: 12px;">
                Your browser does not support iFrames. <a href="{st.session_state.active_pdf_url}">Click here to download PDF</a>
            </iframe>
        """, unsafe_allow_html=True)
        st.markdown("---")

    st.sidebar.markdown("---")
    mode = st.sidebar.radio("Operational Mode:", ["Simulate Dataset User", "Dynamic New User Profile"])

    if mode == "Simulate Dataset User":
        selected_user = st.sidebar.selectbox("Select User ID:", sorted(recommender.ratings_df["User-ID"].unique()))
        user_books = pd.merge(recommender.ratings_df[recommender.ratings_df["User-ID"] == selected_user], recommender.books_df, on="ISBN")
    else:
        selected_user = 9999  
        search_query = st.sidebar.text_input("Search Book Title:", "")
        all_titles = list(recommender.books_df["Book-Title"].dropna().unique()) + [v["title"] for v in amharic_library.values()]
        filtered = [b for b in all_titles if search_query.strip().lower() in str(b).lower()] if search_query else []
        
        if filtered:
            chosen = st.sidebar.selectbox("Select Book:", filtered)
            rating = st.sidebar.slider("Rating (⭐):", 1, 10, 8)
            if st.sidebar.button("Add to Profile"):
                isbn = next((k for k, v in amharic_library.items() if v["title"] == chosen), None) or recommender.books_df[recommender.books_df["Book-Title"] == chosen]["ISBN"].values[0]
                st.session_state.custom_ratings[isbn] = rating
                st.sidebar.success("📌 Added!")

        user_books = pd.DataFrame([
            {"User-ID": 9999, "ISBN": isbn, "Book-Rating": rate, "Book-Title": next((v["title"] for k, v in amharic_library.items() if k == isbn), recommender.books_df[recommender.books_df["ISBN"] == isbn]["Book-Title"].values[0])}
            for isbn, rate in st.session_state.custom_ratings.items()
        ]) if st.session_state.custom_ratings else pd.DataFrame()

        if not user_books.empty:
            recommender.ratings_df = pd.concat([recommender.ratings_df[recommender.ratings_df["User-ID"] != 9999], user_books[["User-ID", "ISBN", "Book-Rating"]]], ignore_index=True)
            recommender.prepare_matrices(); recommender.train()

    num_recommendations = st.sidebar.slider("Recommendations Count:", 1, 10, 5)
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        st.subheader("📖 Interaction History")
        if not user_books.empty:
            for _, row in user_books.iterrows():
                st.write(f"🔹 **{row['Book-Title']}** (⭐ {row['Book-Rating']}/10)")
        else:
            st.info("No active history.")

    with col2:
        st.subheader("✨ AI Recommendations")
        if mode == "Dynamic New User Profile" and user_books.empty:
            st.info("Provide at least one rating.")
        else:
            recommendations = recommender.recommend_books(user_id=int(selected_user), top_n=num_recommendations)
            if recommendations:
                cols = st.columns(3)
                for i, book in enumerate(recommendations):
                    col_idx = i % 3
                    with cols[col_idx]:
                        cover_image = "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=150"
                        
                        # የአማርኛ መጽሐፍ መሆኑን ማረጋገጫ
                        amh_key = None
                        for k, v in amharic_library.items():
                            if book['title'] == v["title"]:
                                amh_key = k
                                cover_image = v["cover"]
                                break

                        st.markdown(f"""
                            <div class='rec-grid-card'>
                                <div class='img-container'><img src='{cover_image}'></div>
                                <div class='rec-title'>{book['title']}</div>
                                <div class='rec-author'>By: {book['author']}</div>
                                <div><span class='score-badge'>🎯 Score: {book['score']:.4f}</span></div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # የአማርኛ ከሆነ አፕሊኬሽኑ ውስጥ ይከፍተዋል፤ እንግሊዘኛ ከሆነ ልክ እንደነበረው ወደ OpenLibrary ይልካል!
                        if amh_key:
                            if st.button(f"📖 ሙሉውን መጽሐፍ እዚሁ አንብብ", key=f"amh_pdf_btn_{i}"):
                                st.session_state.active_pdf_url = amharic_library[amh_key]["pdf_url"]
                                st.session_state.active_pdf_title = amharic_library[amh_key]["title"]   