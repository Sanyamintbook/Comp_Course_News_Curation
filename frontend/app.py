"""
Module: Streamlit Frontend
Purpose: Renders the educational dashboard UI.
Logic:
- Uses a Sidebar for the "Student Profile Builder".
- Sends the profile to the FastAPI backend.
- Receives a unified payload and renders 4 interactive tabs (News, Courses, Competitive, Leisure).
"""
import streamlit as st
import requests
import json
import time

# Base Configuration
st.set_page_config(page_title="NEP 2020 Curation Platform", layout="wide", page_icon="🎓")
API_URL = "http://127.0.0.1:8000/api"

# 0. Admin Upload Panel (Hidden by default, simple toggle)
with st.sidebar.expander("🛠️ Admin Upload Panel"):
    st.title("⚙️ Admin Control Panel")
    st.write("Upload premium courses and competitive materials here. The AI will immediately embed them into the FAISS database.")
    
    target_module = st.selectbox("Target Database Module", ["courses", "competitive", "leisure"])
    uploaded_file = st.file_uploader("Upload JSON Dataset", type=["json"])
    
    if uploaded_file is not None:
        if st.button("Upload to FAISS"):
            with st.spinner(f"AI Gatekeeper is embedding {uploaded_file.name} (this may take a minute)..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/json")}
                    data = {"module": target_module}
                    res = requests.post(f"{API_URL}/admin/upload", files=files, data=data)
                    
                    if res.status_code == 200:
                        st.success(res.json().get("detail", "Upload complete!"))
                    else:
                        st.error(f"Upload failed: {res.text}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {e}")

with st.sidebar.form("profile_form"):
    grade_level = st.selectbox("Grade Level", [
        "Preschool", "Kindergarten", 
        "Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", 
        "Grade 6", "Grade 7", "Grade 8", 
        "Grade 9", "Grade 10", "Grade 11", "Grade 12",
        "Undergrad"
    ])
    target_career = st.text_input("Target Career", value="Doctor")
    fav_subjects_str = st.text_input("Favorite Subjects (comma separated, e.g. Biology, Math)", value="Biology, Geography")
    fav_subjects = [s.strip() for s in fav_subjects_str.split(",") if s.strip()]
    hobbies = st.text_input("Hobbies (comma separated)", value="Drawing, Chess")
    
    submitted = st.form_submit_button("Generate Dashboard", type="primary")

if submitted:
    st.session_state["profile_payload"] = {
        "grade_level": grade_level,
        "target_career": target_career,
        "favorite_subjects": fav_subjects if fav_subjects else ["General"],
        "hobbies": [hobbies]
    }
    
if "profile_payload" not in st.session_state:
    st.session_state["profile_payload"] = {
        "grade_level": grade_level,
        "target_career": target_career,
        "favorite_subjects": fav_subjects if fav_subjects else ["General"],
        "hobbies": [hobbies]
    }

# 2. Main Dashboard (4 Tabs)
tab1, tab2, tab3, tab4 = st.tabs(["📰 News", "📚 Courses", "🏆 Competitive", "🎮 Leisure"])

def render_feed(data_list, tab_name, empty_msg="No curations available for your profile right now."):
    """Helper function to render a list of curations into a tab."""
    if not isinstance(data_list, list) or len(data_list) == 0:
        st.info(empty_msg)
        return
        
    for item in data_list:
        with st.container(border=True):
            st.subheader(item.get("title", "No Title"))
            st.caption(f"📅 {item.get('published', 'Unknown')} | 🏷️ Subject: {item.get('subject', 'General')} | 🎯 Grade: {item.get('grade_level', 'All')}")
            if "distance" in item:
                st.write(f"**Relevance Distance:** `{item.get('distance', 0):.4f}` (Lower is better)")
            
            link = item.get("link")
            if link and link != "None":
                st.write(f"🔗 [Open Link]({link})")

# 3. Independent Module Fetching & Rendering
if "profile_payload" in st.session_state:
    payload = st.session_state.profile_payload
    
    @st.cache_data(show_spinner=False, ttl=600)
    def fetch_module(endpoint, profile_data):
        try:
            res = requests.post(f"{API_URL}/{endpoint}", json=profile_data)
            if res.status_code == 200:
                return res.json()
            elif res.status_code == 403:
                return {"error": f"🛡️ Guardrail Triggered: {res.json().get('detail', 'Inappropriate content blocked.')}"}
            else:
                return {"error": f"Failed to generate {endpoint} curations."}
        except Exception as e:
            return {"error": f"Error connecting to backend: {e}"}

    with tab1:
        with st.spinner("Fetching breaking news..."):
            data = fetch_module("news", payload)
            if isinstance(data, dict) and "error" in data:
                st.error(data["error"])
            else:
                render_feed(data, "news")
                
    with tab2:
        with st.spinner("Curating personalized courses with AI Gatekeeper..."):
            data = fetch_module("courses", payload)
            if isinstance(data, dict) and "error" in data:
                st.error(data["error"])
            else:
                render_feed(data, "courses")
                
    with tab3:
        with st.spinner("Aligning competitive materials with NEP 2020..."):
            data = fetch_module("competitive", payload)
            if isinstance(data, dict) and "error" in data:
                st.error(data["error"])
            else:
                render_feed(data, "competitive")
                
    with tab4:
        with st.spinner("Curating leisure and hobby content..."):
            data = fetch_module("leisure", payload)
            if isinstance(data, dict) and "error" in data:
                st.error(data["error"])
            else:
                render_feed(data, "leisure")
