import json
import streamlit as st
from pathlib import Path

DB_PATH = Path("packaging_knowledge.json")

# Load database
def load_db():
    if DB_PATH.exists():
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {}

# Save database
def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=4)

# ---- Custom CSS for Classy Look ----
st.markdown("""
    <style>
        body {
            background: #f8f9fa;
            font-family: 'Segoe UI', sans-serif;
        }
        .stApp {
            background: linear-gradient(135deg, #f0f2f6, #e4ebf5);
        }
        .big-title {
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
            text-align: center;
            padding-bottom: 10px;
        }
        .success-box {
            background: #eafaf1;
            border-left: 5px solid #2ecc71;
            padding: 10px;
            border-radius: 8px;
        }
        .warning-box {
            background: #fff3cd;
            border-left: 5px solid #ffbb33;
            padding: 10px;
            border-radius: 8px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.markdown("<div class='big-title'>📦 Packaging Knowledge Manager</div>", unsafe_allow_html=True)

# --- Sidebar ---
st.sidebar.title("⚙️ Knowledge Manager")
mode = st.sidebar.radio("Choose Action:", ["View Database", "Add Knowledge", "Edit Knowledge"])

# Load DB
db = load_db()

# --- View Mode ---
if mode == "View Database":
    st.subheader("📖 Current Knowledge Base")
    if db:
        st.json(db)
    else:
        st.markdown("<div class='warning-box'>⚠️ Database is empty.</div>", unsafe_allow_html=True)

# --- Add Mode ---
elif mode == "Add Knowledge":
    st.subheader("➕ Add New Packaging Material")
    name = st.text_input("📌 Packaging Material Name")
    props = st.text_area("📝 Properties")
    best_for = st.text_input("🎯 Best For (comma separated)").split(",")
    cost = st.number_input("💰 Cost per unit", min_value=0)
    emoji = st.text_input("✨ Icon/Emoji (optional)", value="📦")

    if st.button("💾 Save"):
        db[name] = {
            "properties": props,
            "best_for": [x.strip() for x in best_for if x],
            "cost_per_unit": cost,
            "emoji": emoji
        }
        save_db(db)
        st.markdown(f"<div class='success-box'>✅ {name} added successfully!</div>", unsafe_allow_html=True)

# --- Edit Mode ---
elif mode == "Edit Knowledge":
    st.subheader("✏️ Edit Existing Material")
    if db:
        material = st.selectbox("Select material to edit", list(db.keys()))
        if material:
            entry = db[material]
            props = st.text_area("📝 Properties", entry["properties"])
            best_for = st.text_input("🎯 Best For (comma separated)", ",".join(entry["best_for"]))
            cost = st.number_input("💰 Cost per unit", min_value=0, value=entry["cost_per_unit"])
            emoji = st.text_input("✨ Icon/Emoji", entry.get("emoji", "📦"))

            if st.button("🔄 Update"):
                db[material] = {
                    "properties": props,
                    "best_for": [x.strip() for x in best_for.split(",") if x],
                    "cost_per_unit": cost,
                    "emoji": emoji
                }
                save_db(db)
                st.markdown(f"<div class='success-box'>✏️ {material} updated successfully!</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='warning-box'>⚠️ Database is empty.</div>", unsafe_allow_html=True)
