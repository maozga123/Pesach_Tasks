import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# הגדרת העמוד כולל התאמות למובייל
st.set_page_config(
    page_title="נקיונות או לא להיות", 
    page_icon="🧽", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ניהול מצב להפרדה בין מסך פתיחה למסך משימות
if 'show_tasks' not in st.session_state:
    st.session_state.show_tasks = False

# הגדרת משתתפים, צבעים ותמונות ברירת מחדל
PARTICIPANTS = {
    "אבא": {"color": "#4a90e2", "image": "👨", "type": "parent"},
    "מאמו": {"color": "#e24a8d", "image": "👩", "type": "parent"},
    "אליחי": {"color": "#50c878", "image": "👦", "type": "child"},
    "תאיר": {"color": "#ffb347", "image": "👧", "type": "child"},
    "שי": {"color": "#9b59b6", "image": "👶", "type": "child"},
    "גבריאל": {"color": "#34495e", "image": "🧒", "type": "child"}
}

st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style> 
    .stApp { 
        direction: RTL; 
        text-align: right; 
    } 
    
    .main {
        overflow-x: hidden;
    }
    
    /* עיצוב כותרת ראשית של האפליקציה */
    .main-title {
        font-size: clamp(2.5rem, 10vw, 4rem); 
        font-weight: 900;
        text-align: center;
        background: -webkit-linear-gradient(45deg, #2196F3, #4CAF50, #FFC107);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
        padding-bottom: 0px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        line-height: 1.2;
    }
    
    /* כותרת משנה */
    .sub-title {
        font-size: clamp(1.2rem, 5vw, 1.8rem);
        text-align: center;
        color: #555;
        font-weight: 500;
        margin-top: 5px;
        margin-bottom: 30px;
    }
    
    /* רקע ואווירה אביבית עדינה */
    .stApp::before {
        content: "🌸 🦋 🧼 ✨ 🧽 🌷";
        position: fixed;
        top: 10px;
        left: 0;
        width: 100%;
        text-align: center;
        font-size: 2rem;
        opacity: 0.1;
        pointer-events: none;
        z-index: -1;
    }
    
    /* עיצוב כפתור כניסה ענק למובייל */
    .enter-btn-container {
        display: flex;
        justify-content: center;
        margin-top: 50px;
        margin-bottom: 50px;
    }
    
    /* --- עיצוב משימות מותאם במיוחד לנייד למניעת זליגה --- */
    
    /* הכרטיסייה שעוטפת את הטקסט */
    .task-card-content {
        padding: 12px 15px;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 10px;
        width: 100%;
        display: flex;
        align-items: center;
        min-height: 60px;
        box-sizing: border-box; /* חשוב מאוד כדי שהפדינג לא יגדיל את האלמנט מעבר ל-100% */
    }
    
    /* הטקסט בתוך הכרטיסייה */
    .task-text {
        font-size: 1.1em;
        font-weight: 500;
        color: #333;
        word-wrap: break-word;
        white-space: normal; /* מאפשר שבירת שורות טבעית */
        line-height: 1.4;
    }
    
    .completed-task {
        text-decoration: line-through;
        color: #888;
    }
    
    /* פתרון אגרסיבי למניעת שבירת העמודות של Streamlit */
    /* מסתיר את הרווחים ש-Streamlit מוסיף אוטומטית */
    [data-testid="column"] {
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* הופך את הבלוק האופקי ל-Flexbox קשיח */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* בשום אופן לא לשבור שורה! */
        align-items: stretch !important;
        width: 100% !important;
        gap: 0px !important;
    }
    
    /* העמודה של הצ'קבוקס (צד ימין - RTL) */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(1) {
        width: 50px !important;
        flex: 0 0 50px !important; /* גודל קבוע ומוחלט */
        min-width: 50px !important;
        max-width: 50px !important;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    /* העמודה של הטקסט (צד שמאל - RTL) */
    [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child(2) {
        width: calc(100% - 50px) !important;
        flex: 1 1 auto !important; /* לוקח את כל שאר המקום */
        min-width: 0 !important; /* קריטי כדי שהטקסט לא ידחוף את העמודה וישבור שורה */
        padding-left: 5px !important; /* מרווח קטן משמאל כדי למנוע הידבקות לקצה המסך */
    }

    /* כרטיסיות (Flash Cards) בנייד - עיצוב חדש */
    .participant-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        margin-bottom: 20px;
        padding: 20px 15px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        text-align: center;
        width: 100%;
        box-sizing: border-box; /* מונע זליגה מהמסך */
    }
    
    .participant-avatar {
        font-size: clamp(3em, 10vw, 4em);
        background: rgba(255,255,255,0.2);
        border: 3px solid white;
        border-radius: 50%;
        width: clamp(80px, 25vw, 100px);
        height: clamp(80px, 25vw, 100px);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .participant-title {
        margin: 0;
        font-size: clamp(1.5em, 6vw, 2em);
        font-weight: bold;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
        word-break: break-word;
    }
    
    /* מראה של כרטיסיות גולשות (Flash cards) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: flex-start;
        overflow-x: auto;
        -webkit-overflow-scrolling: touch; 
        scrollbar-width: none; 
        padding: 10px 5px;
    }
    
    .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
        display: none; 
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 20px;
        white-space: nowrap;
        background-color: #f8f9fa;
        border-radius: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #eee;
        transition: all 0.2s ease;
    }
    
    /* טאב פעיל */
    .stTabs [aria-selected="true"] {
        background-color: #e3f2fd !important;
        border-color: #2196F3 !important;
        transform: scale(1.05);
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# פונקציות ניווט
def start_cleaning():
    st.session_state.show_tasks = True

def go_home():
    st.session_state.show_tasks = False

# חיבור לשיטס
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    return conn.read(ttl="0s")

# ==========================================
# מסך 1: דף פתיחה
# ==========================================
if not st.session_state.show_tasks:
    st.markdown('<div style="height: 10vh;"></div>', unsafe_allow_html=True) # Spacer
    st.markdown('<div class="main-title">נקיונות או לא להיות! 🧼</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">ג\'רופי מנקים לפסח תשפ"ו ✨</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="enter-btn-container">', unsafe_allow_html=True)
    # כפתור מרכזי ענק בסטרימליט
    if st.button("🚀 לחץ כאן להתחיל לנקות! 🚀", use_container_width=True, type="primary"):
        start_cleaning()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    # תצוגת התקדמות משפחתית כבר בדף הבית
    try:
        df = get_data()
        if 'Status' in df.columns:
            st.divider()
            st.subheader("📊 מצב הבית כרגע:")
            total_done = df['Status'].sum()
            total_tasks = len(df)
            progress = total_done / total_tasks if total_tasks > 0 else 0

            st.write(f"השלמנו {int(progress*100)}% ({int(total_done)} מתוך {total_tasks} משימות)")
            st.progress(progress)
            
            if progress == 1.0 and total_tasks > 0:
                st.balloons()
                st.success("הבית כשר! אפשר להתחיל את הסדר! 🍷")
    except Exception as e:
        pass # במקרה של שגיאה בטעינת נתונים פשוט לא נציג גרף

# ==========================================
# מסך 2: משימות ומשתתפים (Flash Cards)
# ==========================================
else:
    df = get_data()

    if 'Assignee' in df.columns and 'Task' in df.columns and 'Status' in df.columns:
        
        all_names = list(PARTICIPANTS.keys())
        
        if not df.empty:
            sheet_names = df['Assignee'].dropna().unique().tolist()
            for name in sheet_names:
                if name not in all_names and name.strip() != "":
                    all_names.append(name)
                    PARTICIPANTS[name] = {"color": "#95a5a6", "image": "👤", "type": "other"}
                
        # --- העברת הוספת משימה לתוך expander במקום sidebar כדי למנוע כתיבה אנכית במובייל ---
        with st.expander("➕ הוספת משימה חדשה", expanded=False):
            with st.form("add_task_form"):
                new_task_desc = st.text_input("תיאור המשימה")
                new_task_assignee = st.selectbox("למי לשייך?", all_names)
                submitted = st.form_submit_button("הוסף משימה", use_container_width=True)
                
                if submitted:
                    if new_task_desc:
                        new_row = pd.DataFrame([{'Assignee': new_task_assignee, 'Task': new_task_desc, 'Status': False}])
                        updated_df = pd.concat([df, new_row], ignore_index=True)
                        conn.update(data=updated_df)
                        st.toast("המשימה נוספה בהצלחה! 🎉")
                        st.rerun()
                    else:
                        st.warning("יש להזין תיאור למשימה")

        # כותרת קטנה למעלה
        st.markdown('<div style="text-align:center; color:#888; margin-bottom:10px;">החלק ימינה/שמאלה בין השמות ↔️</div>', unsafe_allow_html=True)
        
        # Tabs כ-Flash Cards
        tabs = st.tabs(all_names)
        
        for i, tab in enumerate(tabs):
            user = all_names[i]
            
            with tab:
                user_info = PARTICIPANTS.get(user, {"color": "#95a5a6", "image": "👤"})
                user_color = user_info["color"]
                user_avatar = user_info["image"]
                
                # תחילת ה-Flash Card של המשתמש (מכיל את הכותרת והמשימות ביחד)
                st.markdown(f"""
                <div class="participant-header" style="background-color: {user_color};">
                    <div class="participant-avatar">{user_avatar}</div>
                    <h2 class="participant-title">המשימות של {user}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                user_tasks = df[df['Assignee'] == user].copy()
                
                if user_tasks.empty:
                    st.info(f"ל-{user} אין כרגע משימות. איזה כיף לו/לה! 🎉")
                else:
                    # יצירת מרווח בין הכותרת למשימות
                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    
                    for index, row in user_tasks.iterrows():
                        # שימוש ב-st.columns ליצירת שורה אחת של צ'קבוקס וטקסט
                        # עדכנתי את היחסים לטובת כרטיסיית הטקסט
                        col1, col2 = st.columns([1, 10])
                        
                        with col1:
                             status_val = bool(row['Status']) if pd.notna(row['Status']) else False
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
                                 border_color = user_color 
                                 text_class = ""
                            
                             st.markdown(f"""
                             <div style="background-color: {bg_color}; border-right: 5px solid {border_color};" class="task-card-content">
                                 <div class="task-text {text_class}">
                                     {row['Task']}
                                 </div>
                             </div>
                             """, unsafe_allow_html=True)
                     
    else:
        st.error("לא נמצאו עמודות מתאימות בגיליון (Assignee, Task, Status). נא לבדוק את קובץ הגוגל שיטס.")
    
    st.divider()
    if st.button("🏠 חזרה למסך הפתיחה", use_container_width=True):
        go_home()
        st.rerun()