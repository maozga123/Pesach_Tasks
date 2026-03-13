import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="ניקיונות פסח משפחתיים", page_icon="🧹", layout="centered")

# עיצוב בסיסי בעברית
st.markdown("""<style> .stApp { direction: RTL; text-align: right; } </style>""", unsafe_allow_html=True)

st.title("🧹 מבצע פסח: הבית של משפחת גרופי")

# חיבור לשיטס
conn = st.connection("gsheets", type=GSheetsConnection)

# פונקציה לקריאת נתונים (עם Cache כדי שלא יטען כל פעם)
def get_data():
    return conn.read(ttl="0s") # ttl=0 מבטיח ריענון מיידי

df = get_data()

# בחירת שם הילד
names = df['Assignee'].unique().tolist()
user = st.selectbox("מי מנקה עכשיו?", names)

# סינון משימות לפי המשתמש
user_tasks = df[df['Assignee'] == user].copy()

st.subheader(f"המשימות של {user}:")

# תצוגת המשימות עם אפשרות סימון
for index, row in user_tasks.iterrows():
    is_done = st.checkbox(row['Task'], value=row['Status'], key=f"task_{index}")
    # כאן אפשר להוסיף לוגיקה לעדכון ה-Sheet אם רוצים Persistence מלא
    # הערה: לעדכון כתיבה ל-Sheets תצטרך להגדיר הרשאות כתיבה ב-Secrets

# גרף התקדמות משפחתי
st.divider()
total_done = df['Status'].sum()
total_tasks = len(df)
progress = total_done / total_tasks

st.write(f"התקדמות כללית: {int(progress*100)}%")
st.progress(progress)

if progress == 1.0:
    st.balloons()
    st.success("הבית כשר! אפשר להתחיל את הסדר!")