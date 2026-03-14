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

    /* --- הפתרון החדש והאולטימטיבי למשימות במובייל --- */
    /* במקום להשתמש בעמודות שקורסות, אנחנו מעצבים את הצ'קבוקס הטבעי של סטרימליט ככרטיסייה! */
    
    div[data-testid="stCheckbox"] {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        
        /* מרכוז מוחלט וקביעת רוחב! */
        margin: 0 auto 12px auto !important; 
        width: 90% !important;
        max-width: 400px !important;
        
        border-right: 5px solid #ff9800; /* ברירת מחדל: כתום למשימה פתוחה */
        transition: all 0.3s ease;
        display: flex !important;
        align-items: center;
    }
    
    /* עיצוב הטקסט בתוך הצ'קבוקס */
    div[data-testid="stCheckbox"] label {
        cursor: pointer;
        width: 100%;
    }
    
    div[data-testid="stCheckbox"] label div[data-testid="stMarkdownContainer"] p {
        font-size: 1.15em;
        font-weight: 500;
        color: #333;
        margin: 0;
        padding-right: 10px; /* מרווח בין הוי לטקסט */
    }
    
    /* הגדלת ריבוע הוי עצמו כדי שיהיה נוח ללחיצה באצבע */
    div[data-testid="stCheckbox"] input {
        transform: scale(1.4);
    }
    
    /* שינוי עיצוב הכרטיסייה כאשר המשימה בוצעה (נתמך ברוב הדפדפנים המודרניים בנייד) */
    div[data-testid="stCheckbox"]:has(input:checked) {
        background-color: #f0fdf4 !important; /* ירוק חלש */
        border-right-color: #4caf50 !important; /* ירוק חזק */
        opacity: 0.8;
    }
    
    /* הוספת קו חוצה לטקסט כאשר בוצע */
    div[data-testid="stCheckbox"]:has(input:checked) label div[data-testid="stMarkdownContainer"] p {
        text-decoration: line-through;
        color: #888;
    }

    /* --- כרטיסיית המשתתף (Header) --- */
    .participant-header {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 10px;
        
        /* מרכוז מוחלט תואם לרוחב המשימות */
        margin: 0 auto 20px auto !important; 
        width: 90% !important; 
        max-width: 400px !important;
        
        padding: 20px 15px;
        border-radius: 15px;
        color: white;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        text-align: center;
        box-sizing: border-box;
    }
    
    .participant-avatar {
        font-size: clamp(2.5em, 8vw, 3.5em);
        background: rgba(255,255,255,0.2);
        border: 3px solid white;
        border-radius: 50%;
        width: clamp(70px, 20vw, 90px);
        height: clamp(70px, 20vw, 90px);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .participant-title {
        margin: 0;
        font-size: clamp(1.3em, 5vw, 1.8em);
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
                
        # --- העברת הוספת משימה לתוך expander ---
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
                
                # עיצוב מרכזי של תמונת הפרופיל והכותרת
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
                    for index, row in user_tasks.iterrows():
                        # קריאת הסטטוס
                        status_val = bool(row['Status']) if pd.notna(row['Status']) else False
                        
                        # גיבוי למחיקת טקסט במכשירים ישנים (שימוש ב-Markdown של סטרימליט)
                        task_text = f"~~{row['Task']}~~" if status_val else row['Task']
                        
                        # --- הפתרון האולטימטיבי: שימוש בצ'קבוקס הטבעי של סטרימליט בלבד! ---
                        # זה מבטיח שהוי והטקסט תמיד, אבל תמיד, יישארו ביחד בשורה אחת על כל מסך.
                        is_done = st.checkbox(
                            task_text, 
                            value=status_val, 
                            key=f"task_{index}_{user}"
                        )
                        
                        if is_done != status_val:
                            df.at[index, 'Status'] = is_done
                            conn.update(data=df)
                            st.toast("הסטטוס עודכן! 💾")
                            st.rerun()
                     
    else:
        st.error("לא נמצאו עמודות מתאימות בגיליון (Assignee, Task, Status). נא לבדוק את קובץ הגוגל שיטס.")
    
    st.divider()
    if st.button("🏠 חזרה למסך הפתיחה", use_container_width=True):
        go_home()
        st.rerun()