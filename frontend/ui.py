import streamlit as st
import requests
import time

# Page Config
st.set_page_config(page_title="ActionExtract AI (Smart)", page_icon="🧠", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 100%);
        color: #e0e0e0;
        font-family: 'Inter', sans-serif;
    }
    
    .transcript-box {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 20px;
        height: 350px;
        overflow-y: auto;
        font-family: 'Courier New', monospace;
        font-size: 0.9rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .transcript-line { margin-bottom: 8px; border-bottom: 1px dashed rgba(255,255,255,0.1); }
    
    .action-card {
        background: rgba(0, 198, 255, 0.05);
        border: 1px solid rgba(0, 198, 255, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        transition: all 0.2s;
    }
    .action-card.done {
        background: rgba(46, 204, 113, 0.1);
        border-color: rgba(46, 204, 113, 0.4);
        opacity: 0.7;
    }
    
    .note-card {
        background: rgba(241, 196, 15, 0.05);
        border: 1px solid rgba(241, 196, 15, 0.2);
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        color: #f1c40f;
    }

    </style>
""", unsafe_allow_html=True)

st.title("🧠 ActionExtract AI · Smart Analyzer")

# Sidebar
with st.sidebar:
    st.header("Input Area")
    with st.form("input_form"):
        user_input = st.text_area("Transcript / Notes", height=200, placeholder="Paste dialogue here...")
        submitted = st.form_submit_button("Analyze", type="primary", use_container_width=True)
        if submitted and user_input:
            try:
                res = requests.post("http://localhost:5000/process_text", json={"text": user_input})
                if res.status_code == 200:
                    st.success("Analysis Complete!")
                else:
                    st.error("Error processing.")
            except Exception as e:
                st.error(f"Backend Error: {e}")
                
    if st.button("Reset Session", type="secondary"):
        requests.post("http://localhost:5000/reset")
        st.rerun()

# Layout
col1, col2, col3 = st.columns([1, 1, 1])

# Fetch data
try:
    status_res = requests.get("http://localhost:5000/status")
    data = status_res.json() if status_res.status_code == 200 else {}
    transcript_lines = data.get("transcript", [])
    action_items = data.get("action_items", [])
    important_notes = data.get("important_notes", [])
except:
    transcript_lines = []
    action_items = []
    important_notes = []

with col1:
    st.subheader("📜 Transcript")
    st.markdown('<div class="transcript-box">', unsafe_allow_html=True)
    if not transcript_lines: st.markdown("*Empty...*")
    for line in transcript_lines:
        st.markdown(f'<div class="transcript-line">{line}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.subheader("✅ Action Items")
    if not action_items: st.info("No tasks yet.")
    
    for idx, item in enumerate(action_items):
        is_done = item.get('done', False)
        
        # Container for the card
        with st.container():
            # Apply styling via markdown (Streamlit limitations on div wrapping native widgets)
            # We used a trick: custom markdown card, but button separately? 
            # Better: Use st.columns inside the loop for the checkbox
            
            c_check, c_content = st.columns([0.15, 0.85])
            with c_check:
                # Toggle Button
                if st.button("✓", key=f"btn_{idx}", type="primary" if is_done else "secondary"):
                    requests.post("http://localhost:5000/toggle_task", json={"index": idx})
                    st.rerun()
            
            with c_content:
                # Visual
                style_class = "action-card done" if is_done else "action-card"
                st.markdown(f"""
                <div class="{style_class}">
                    <b>👤 {item.get('owner', 'Unassigned')}</b> <span style="font-size:0.8em; opacity:0.7">📅 {item.get('deadline', 'No Date')}</span><br>
                    {item.get('task', 'Unknown')}
                </div>
                """, unsafe_allow_html=True)


with col3:
    st.subheader("📌 Important Notes")
    if not important_notes: st.info("No notes yet.")
    for note in reversed(important_notes):
        st.markdown(f'<div class="note-card">🔸 {note}</div>', unsafe_allow_html=True)

