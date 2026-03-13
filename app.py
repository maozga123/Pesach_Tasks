import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="ניקיונות פסח משפחתיים", page_icon="🧹", layout="centered")

# עיצוב בסיסי בעברית עם התאמות לכרטיסיות
st.markdown("""
<style> 
    .stApp { 
        direction: RTL; 
        text-align: right; 
    } 
    
    /* עיצוב כרטיסייה */
    .task-card-content {
        padding: 10px;
        border-radius: 8px;
        margin-right: 10px; /* מרווח מהצ'קבוקס */
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* טקסט משימה */
    .task-text {
        font-size: 1.1em;
        font-weight: 500;
        color: #333;
    }
    
    .completed-task {
        text-decoration: line-through;
        color: #888;
    }
    
    /* יישור אנכי של הצ'קבוקס */
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧹 מבצע פסח: הבית של משפחת גרופי")

# חיבור לשיטס
conn = st.connection("gsheets", type=GSheetsConnection)

# פונקציה לקריאת נתונים (עם Cache כדי שלא יטען כל פעם)
def get_data():
    return conn.read(ttl="0s") # ttl=0 מבטיח ריענון מיידי

df = get_data()

# בחירת שם הילד
if 'Assignee' in df.columns:
    names = df['Assignee'].dropna().unique().tolist()
    user = st.selectbox("מי מנקה עכשיו?", names)

    # סינון משימות לפי המשתמש
    user_tasks = df[df['Assignee'] == user].copy()

    st.subheader(f"המשימות של {user}:")

    # תצוגת המשימות - רפקטור לתצוגת כרטיסיות
    for index, row in user_tasks.iterrows():
        # שימוש ב-container לכל משימה
        with st.container():
            # חלוקה לעמודות: צ'קבוקס | תוכן המשימה
            # ב-RTL עמודה 1 היא הימנית ביותר
            col1, col2 = st.columns([0.15, 0.85])
            
            with col1:
                 # שימוש בצ'קבוקס לשינוי סטטוס
                 # המרת סטטוס לבוליאני למניעת שגיאות
                 status_val = bool(row['Status']) if pd.notna(row['Status']) else False
                 is_done = st.checkbox("", value=status_val, key=f"task_{index}")
                 
            with col2:
                 # קביעת סגנון דינמי לפי הסטטוס (כולל אינטראקציה מיידית)
                 if is_done:
                     bg_color = "#f0fdf4" # ירוק בהיר מאוד
                     border_color = "#4caf50" # ירוק
                     text_class = "completed-task"
                 else:
                     bg_color = "#ffffff"
                     border_color = "#ff9800" # כתום
                     text_class = ""
                
                 # כרטיסייה מעוצבת באמצעות HTML
                 st.markdown(f"""
                 <div style="background-color: {bg_color}; border-right: 5px solid {border_color};" class="task-card-content">
                     <div class="task-text {text_class}">
                         {row['Task']}
                     </div>
                 </div>
                 """, unsafe_allow_html=True)
                 
    # גרף התקדמות משפחתי
    st.divider()
    if 'Status' in df.columns:
        total_done = df['Status'].sum()
        total_tasks = len(df)
        progress = total_done / total_tasks if total_tasks > 0 else 0

        st.write(f"התקדמות כללית: {int(progress*100)}%")
        st.progress(progress)

        if progress == 1.0:
            st.balloons()
            st.success("הבית כשר! אפשר להתחיל את הסדר!")
else:
    st.error("לא נמצאו עמודות מתאימות בגיליון (Assignee, Task, Status)")
