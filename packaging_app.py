import streamlit as st
import json
import os

DB_FILE = "packaging_db.json"

# --- Utility functions ---
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {"materials": {}, "mindmap": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load_db()

# --- PAGE CONFIG ---
st.set_page_config(page_title="⚡ Futuristic Packaging Advisor", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
    color: #E0E0E0;
    font-family: 'Segoe UI', sans-serif;
}

/* Titles */
h1, h2, h3 {
    color: #00ffe7;
    text-shadow: 0px 0px 15px #00ffe7;
}

/* Cards */
.block-container {
    border-radius: 15px;
    padding: 20px;
}

/* Input fields */
.stTextInput>div>div>input,
.stTextArea textarea {
    background: rgba(255,255,255,0.1);
    border: 1px solid #00ffe7;
    border-radius: 10px;
    color: #fff;
}

.stTextInput>div>div>input:focus,
.stTextArea textarea:focus {
    border: 1px solid #ff00ff;
    box-shadow: 0px 0px 10px #ff00ff;
}

/* Buttons */
.stButton>button {
    background: linear-gradient(90deg, #00ffe7, #ff00ff);
    color: black;
    font-weight: bold;
    border-radius: 12px;
    padding: 10px 20px;
    border: none;
    transition: 0.3s;
}
.stButton>button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 15px #ff00ff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(12px);
}
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("⚡ Navigation")
page = st.sidebar.radio("Choose a section:", ["🛒 Product Advisor", "📚 Teach Model", "📂 Database Viewer"])

# ---------------- PRODUCT ADVISOR ----------------
if page == "🛒 Product Advisor":
    st.title("🛒 Futuristic Product Advisor")

    col1, col2 = st.columns(2)
    with col1:
        product_name = st.text_input("🔖 Product Name", key="prod_name")
    with col2:
        packaging_type = st.selectbox("📦 Packaging Type", ["Primary", "Secondary", "Tertiary"], key="pack_type")

    product_desc = st.text_area("📝 Product Description", key="prod_desc", height=150)

    if st.button("🚀 Suggest Packaging", key="suggest_btn"):
        if product_name and product_desc:
            st.success(f"✨ Suggested packaging for **{product_name}**:")

            if "fragile" in product_desc.lower():
                st.markdown("🫙 **Glass** with protective cushioning → 📦 Corrugated Box")
            elif "food" in product_desc.lower():
                st.markdown("🥫 **Multilayer Laminates** or 🍃 **Plastic Films** (Food grade)")
            else:
                st.markdown("📦 **Standard Corrugated Fiberboard**")

            st.balloons()
        else:
            st.warning("⚠️ Please enter product details first!")

# ---------------- TEACH MODEL ----------------
elif page == "📚 Teach Model":
    st.title("📚 Teach the AI Model")

    st.markdown("💡 Here you can **teach** the advisor about new packaging materials, categories, or rules.")

    with st.expander("➕ Add New Material / Category"):
        c_name = st.text_input("Material / Category Name", key="teach_cname")
        c_desc = st.text_area("Description", key="teach_cdesc")
        c_notes = st.text_area("Notes (optional)", key="teach_notes")

        if st.button("💾 Save Category", key="save_category_btn"):
            if c_name:
                db["materials"][c_name] = {
                    "description": c_desc,
                    "notes": c_notes
                }
                save_db(db)
                st.success(f"✅ Taught model about **{c_name}**")
            else:
                st.warning("⚠️ Please enter a category name!")

    with st.expander("🧠 Update Mind Map"):
        mm_level = st.selectbox("Packaging Level", ["Primary", "Secondary", "Tertiary"], key="teach_level")
        mm_notes = st.text_area("Mind Map Notes", key="teach_mm_notes")

        if st.button("💾 Save Mind Map", key="save_mm_btn"):
            db["mindmap"][mm_level] = mm_notes
            save_db(db)
            st.success(f"✅ Updated mind map for {mm_level} packaging")

# ---------------- DATABASE VIEWER ----------------
elif page == "📂 Database Viewer":
    st.title("📂 Knowledge Database")

    st.markdown("🔍 Below is the **entire JSON knowledge database** currently stored in your model.")

    st.json(db, expanded=True)

    st.download_button(
        label="📥 Download Database (JSON Backup)",
        data=json.dumps(db, indent=4),
        file_name="packaging_db.json",
        mime="application/json",
        key="download_db_btn"
    )
