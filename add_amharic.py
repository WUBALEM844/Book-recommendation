import pandas as pd

books_path = "book-dataset/Books.csv"

try:
    # Read with UTF-8 to support Amharic characters safely
    books_df = pd.read_csv(books_path, low_memory=False, encoding="utf-8")
    
    # Ethiopian literature masterpieces
    amharic_books = [
        {
            "ISBN": "AMH001",
            "Book-Title": "ፍቅር እስከ መቃብር",
            "Book-Author": "ሐዲስ አለማየሁ",
            "Year-Of-Publication": 1965,
            "Publisher": "Berhanena Selam"
        },
        {
            "ISBN": "AMH002",
            "Book-Title": "የእኔ ማስታወሻ",
            "Book-Author": "ስብሐት ገብረእግዚአብሔር",
            "Year-Of-Publication": 2001,
            "Publisher": "Mega Publishing"
        },
        {
            "ISBN": "AMH003",
            "Book-Title": "የሐበሻ ጀብዱ",
            "Book-Author": "ይልማ ደሬሳ",
            "Year-Of-Publication": 1970,
            "Publisher": "Artistic Printing Press"
        }
    ]
    
    amharic_df = pd.DataFrame(amharic_books)
    
    # Append and Save strictly using UTF-8 encoding
    updated_books_df = pd.concat([books_df, amharic_df], ignore_index=True)
    updated_books_df.to_csv(books_path, index=False, encoding="utf-8")
    print("🎯 Success: Masterpieces injected into Books.csv with clean UTF-8 Amharic text!")

except Exception as e:
    print(f"❌ Error: {e}")