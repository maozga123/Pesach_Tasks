import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

st.set_page_config(page_title="ניקיונות פסח משפחתיים", page_icon="🧹", layout="centered")

# הגדרת משתתפים, צבעים ותמונות ברירת מחדל (אפשר לשנות שמות בהתאם לגיליון)
PARTICIPANTS = {
    "אבא": {"color": "#4a90e2", "image": "👨", "type": "parent"},
    "מאמו": {"color": "#e24a8d", "image": "👩", "type": "parent"},
    "אליחי": {"color": "#50c878", "image": "👦", "type": "child"},
    "תאיר": {"color": "#ffb347", "image": "👧", "type": "child"},
    "שי": {"color": "#9b59b6", "image": "👶", "type": "child"},
    "גבריאל": {"color": "#34495e", "image": "🧒", "type": "child"}
}

# עיצוב בסיסי בעברית עם התאמות לכרטיסיות
st.markdown("""
<style> 
    .stApp { 
        direction: RTL; 
        text-align: right; 
    } 
    
    /* עיצוב כרטיסייה למשימה */
    .task-card-content {
        padding: 10px;
        border-radius: 8px;
        margin-right: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 5px;
    }
    
    .task-text {
        font-size: 1.1em;
        font-weight: 500;
        color: #333;
    }
    
    .completed-task {
        text-decoration: line-through;
        color: #888;
    }
    
    div[data-testid="column"] {
        display: flex;
        align-items: center;
    }
    
    /* סגנון כותרת משתתף */
    .participant-header {
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
        padding: 15px;
        border-radius: 10px;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .participant-avatar {
        font-size: 2.5em;
        background: rgba(255,255,255,0.2);
        border: 2px solid white;
        border-radius: 50%;
        width: 70px;
        height: 70px;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }
    
    .participant-title {
        margin: 0;
        font-size: 1.8em;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    }
    
    /* יישור טאבים לימין */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: flex-start;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧹 מבצע פסח: הבית של משפחת גרופי")

# חיבור לשיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="0s")

df = get_data()

if 'Assignee' in df.columns and 'Task' in df.columns and 'Status' in df.columns:
    
    # וידוא שכל מי שמוגדר במילון קיים ברשימה
    all_names = list(PARTICIPANTS.keys())
    
    # הוספת שמות מהגיליון שלא הוגדרו במילון כברירת מחדל
    if not df.empty:
        sheet_names = df['Assignee'].dropna().unique().tolist()
        for name in sheet_names:
            if name not in all_names and name.strip() != "":
                all_names.append(name)
                PARTICIPANTS[name] = {"color": "#95a5a6", "image": "👤", "type": "other"}
            
    # --- סרגל צד להוספת משימות ---
    with st.sidebar:
        st.header("➕ הוספת משימה חדשה")
        with st.form("add_task_form"):
            new_task_desc = st.text_input("תיאור המשימה")
            new_task_assignee = st.selectbox("למי לשייך?", all_names)
            submitted = st.form_submit_button("הוסף משימה")
            
            if submitted:
                if new_task_desc:
                    new_row = pd.DataFrame([{'Assignee': new_task_assignee, 'Task': new_task_desc, 'Status': False}])
                    updated_df = pd.concat([df, new_row], ignore_index=True)
                    conn.update(data=updated_df)
                    st.toast("המשימה נוספה בהצלחה! 🎉")
                    st.rerun()
                else:
                    st.warning("יש להזין תיאור למשימה")

    # --- תצוגה באמצעות Tabs ---
    # יצירת כרטיסיות (Tabs) לכל משתתף
    tabs = st.tabs(all_names)
    
    for i, tab in enumerate(tabs):
        user = all_names[i]
        
        with tab:
            user_info = PARTICIPANTS.get(user, {"color": "#95a5a6", "image": "👤"})
            user_color = user_info["color"]
            user_avatar = user_info["image"]
            
            # כותרת אישית מעוצבת למשתתף
            st.markdown(f"""
            <div class="participant-header" style="background-color: {user_color};">
                <div class="participant-avatar">{user_avatar}</div>
                <h2 class="participant-title">המשימות של {user}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            # סינון משימות לפי המשתמש
            user_tasks = df[df['Assignee'] == user].copy()
            
            if user_tasks.empty:
                st.info(f"ל-{user} אין כרגע משימות. איזה כיף לו/לה! 🎉")
            else:
                for index, row in user_tasks.iterrows():
                    with st.container():
                        col1, col2 = st.columns([0.15, 0.85])
                        
                        with col1:
                             status_val = bool(row['Status']) if pd.notna(row['Status']) else False
                             # מפתח ייחודי שכולל גם אינדקס וגם שם למניעת כפילויות במעברים מהירים
                             is_done = st.checkbox("", value=status_val, key=f"task_{index}_{user}")
                             
                             if is_done != status_val:
                                 df.at[index, 'Status'] = is_done
                                 conn.update(data=df)
                                 st.toast("הסטטוס עודכן! 💾")
                                 st.rerun()
                             
                        with col2:
                             if is_done:
                                 bg_color = "#f0fdf4"
                                 border_color = "#4caf50"
                                 text_class = "completed-task"
                             else:
                                 bg_color = "#ffffff"
                                 border_color = user_color # שימוש בצבע המשתתף למשימות פתוחות
                                 text_class = ""
                            
                             st.markdown(f"""
                             <div style="background-color: {bg_color}; border-right: 5px solid {border_color};" class="task-card-content">
                                 <div class="task-text {text_class}">
                                     {row['Task']}
                                 </div>
                             </div>
                             """, unsafe_allow_html=True)
                 
    # גרף התקדמות משפחתי
    st.divider()
    st.subheader("📊 מדד התקדמות משפחתי")
    
    total_done = df['Status'].sum()
    total_tasks = len(df)
    progress = total_done / total_tasks if total_tasks > 0 else 0

    st.write(f"התקדמות כללית: {int(progress*100)}% ({int(total_done)}/{total_tasks} משימות)")
    st.progress(progress)

    if progress == 1.0 and total_tasks > 0:
        st.balloons()
        st.success("הבית כשר! אפשר להתחיל את הסדר! 🍷🍷🍷🍷")
else:
    st.error("לא נמצאו עמודות מתאימות בגיליון (Assignee, Task, Status). נא לבדוק את קובץ הגוגל שיטס.")