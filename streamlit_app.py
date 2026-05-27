import streamlit as st
import pandas as pd
import numpy as np
from app import BookRecommender
import os

# ==============================================================================
# EASY AMHARIC DATA & STORIES (INTERNAL - NO EXTERNAL LINKS TO BREAK!)
# ==============================================================================
local_metadata = {
    "AMH001": {
        "title": "Clean ፍቅር እስከ መቃብር", 
        "author": "ሐዲስ አለማየሁ", 
        "story": "ፍቅር እስከ መቃብር በኢትዮጵያ ሥነ-ጽሑፍ ውስጥ ትልቅ ቦታ ያለውና የቦጋለ እና የሰበላን እውነተኛ ፍቅር፣ የህብረተሰቡን የክፍፍል ባህል የሚተርክ ድንቅ መጽሐፍ ነው።"
    },
    "AMH002": {
        "title": "የእኔ ማስታወሻ", 
        "author": "ስብሐት ገብረእግዚአብሔር", 
        "story": "የደራሲ ስብሐት ገብረእግዚአብሔር ሕይወት፣ ፍልስፍና እና የዕለት ተዕለት ትዝታዎች ግልጽ እና ማራኪ በሆነ የቋንቋ ስልት የተጻፈበት መጽሐፍ ነው።"
    },
    "AMH003": {
        "title": "የሐበሻ ጀብዱ", 
        "author": "ይልማ ደሬሳ", 
        "story": "ስለ ኢትዮጵያ ታሪክ፣ ጀግንነት እና ማኅበራዊ ሕይወት ሰፊ ትንታኔ የሚሰጥ የታሪክ እና የሥነ-ጽሑፍ መጽሐፍ ነው።"
    },
    "AMH004": {
        "title": "ኦሮማይ", 
        "author": "በአሉ ግርማ", 
        "story": "ኦሮማይ በበዓሉ ግርማ የተጻፈና በታሪካዊው የቀይ ኮከብ ዘመቻ ወቅት በኤርትራ የነበረውን እውነተኛ የፖለቲካ እና የማኅበራዊ ሕይወት ውጥረት የሚተርክ ድንቅ ልብወለድ ነው።"
    }
}

def inject_amharic_masterpieces():
    books_path = "book-dataset/Books.csv"
    if os.path.exists(books_path):
        try:
            df = pd.read_csv(books_path, low_memory=False, encoding="utf-8")
            if not df["ISBN"].str.contains("AMH001", na=False).any():
                amharic_books = [
                    {"ISBN": k, "Book-Title": v["title"], "Book-Author": v["author"], "Year-Of-Publication": 1980, "Publisher": "Local"}
                    for k, v in local_metadata.items()
                ]
                updated_df = pd.concat([df, pd.DataFrame(amharic_books)], ignore_index=True)
                updated_df.to_csv(books_path, index=False, encoding="utf-8")
        except Exception:
            pass

inject_amharic_masterpieces()
# ==============================================================================

st.set_page_config(page_title="Smart Book System", page_icon="📚", layout="wide")

@st.cache_resource
def load_recommender():
    engine = BookRecommender()
    engine.run_pipeline()
    return engine

try:
    recommender = load_recommender()
    
    st.markdown('<h1 style="text-align:center; color:#2563EB;">📚 Smart Book Recommendation System</h1>', unsafe_allow_html=True)
    st.markdown("---")

    if "custom_ratings" not in st.session_state:
        st.session_state.custom_ratings = {}

    # SIDEBAR - READ INTERNAL BOOK STORIES IMMEDIATELY
    st.sidebar.header("📖 Read Amharic Books")
    selected_book = st.sidebar.selectbox("እዚህ አፕ ላይ ማንበብ የሚፈልጉትን መጽሐፍ ይምረጡ:", ["-- ይምረጡ --"] + [v["title"] for v in local_metadata.values()])
    
    if selected_book != "-- ይምረጡ --":
        for v in local_metadata.values():
            if v["title"] == selected_book:
                st.sidebar.info(f"✍️ **ደራሲ:** {v['author']}\n\n📖 **ስለ መጽሐፉ:** {v['story']}")

    st.sidebar.markdown("---")
    mode = st.sidebar.radio("የተጠቃሚ ሁኔታ (Mode):", ["Simulate Dataset User", "Dynamic New User Profile"])

    if mode == "Simulate Dataset User":
        selected_user = st.sidebar.selectbox("User ID ካለው ዳታሴት ይምረጡ:", sorted(recommender.ratings_df["User-ID"].unique()))
        user_books = pd.merge(recommender.ratings_df[recommender.ratings_df["User-ID"] == selected_user], recommender.books_df, on="ISBN")
    else:
        selected_user = 9999
        search_query = st.sidebar.text_input("የመጽሐፍ ርዕስ ይፈልጉ:", "")
        all_titles = list(recommender.books_df["Book-Title"].dropna().unique()) + [v["title"] for v in local_metadata.values()]
        
        filtered = [b for b in all_titles if search_query.strip().lower() in str(b).lower()] if search_query else []
        
        if filtered:
            chosen = st.sidebar.selectbox("መጽሐፉን ከዝርዝሩ ውስጥ ይምረጡ:", filtered)
            rating = st.sidebar.slider("ደረጃ ይስጡ (⭐):", 1, 10, 8)
            if st.sidebar.button("ወደ ፕሮፋይል ጨምር"):
                isbn = next((k for k, v in local_metadata.items() if v["title"] == chosen), None) or recommender.books_df[recommender.books_df["Book-Title"] == chosen]["ISBN"].values[0]
                st.session_state.custom_ratings[isbn] = rating
                st.sidebar.success(f"📌 '{chosen}' ተመዝግቧል!")
        
        user_books = pd.DataFrame([
            {"User-ID": 9999, "ISBN": isbn, "Book-Rating": rate, "Book-Title": next((v["title"] for k, v in local_metadata.items() if k == isbn), recommender.books_df[recommender.books_df["ISBN"] == isbn]["Book-Title"].values[0])}
            for isbn, rate in st.session_state.custom_ratings.items()
        ]) if st.session_state.custom_ratings else pd.DataFrame()

        if not user_books.empty:
            recommender.ratings_df = pd.concat([recommender.ratings_df[recommender.ratings_df["User-ID"] != 9999], user_books[["User-ID", "ISBN", "Book-Rating"]]], ignore_index=True)
            recommender.prepare_matrices(); recommender.train()

    # MAIN WINDOW DISPLAY
    col1, col2 = st.columns([1, 2], gap="medium")
    
    with col1:
        st.subheader("📖 የእርስዎ የታዩ መጻሕፍት")
        if not user_books.empty:
            for _, row in user_books.iterrows():
                st.write(f"🔹 **{row['Book-Title']}** — (⭐ {row['Book-Rating']}/10)")
        else:
            st.info("እባክዎ በግራ በኩል መጽሐፍ ፈልገው ደረጃ ይስጡ።")

    with col2:
        st.subheader("✨ የ AI መጽሐፍ ምክረ ሃሳብ")
        if mode == "Dynamic New User Profile" and user_books.empty:
            st.info("ምክረ ሃሳብ ለማግኘት ቢያንስ አንድ መጽሐፍ ደረጃ ይስጡ።")
        else:
            recs = recommender.recommend_books(user_id=int(selected_user), top_n=4)
            if recs:
                for b in recs:
                    with st.container():
                        st.markdown(f"""
                        <div style='background-color:white; padding:15px; border-radius:10px; margin-bottom:10px; border:1px solid #E2E8F0;'>
                            <h4 style='margin:0; color:#0F172A;'>📘 {b['title']}</h4>
                            <p style='margin:4px 0; color:#64748B; font-size:13px;'>ደራሲ: {b['author']}</p>
                            <span style='background-color:#ECFDF5; color:#059669; padding:2px 6px; border-radius:5px; font-size:12px; font-weight:bold;'>🎯 AI Score: {b['score']:.4f}</span>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.warning("ምንም ተዛማጅ አልተገኘም።")

except Exception as e:
    st.error(f"Error: {e}")