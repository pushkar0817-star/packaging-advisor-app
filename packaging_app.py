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

# --- UI ---
st.set_page_config(page_title="📦 Packaging Advisor", layout="wide")

st.title("📦 Packaging Advisor App")

tabs = st.tabs(["Product Advisor", "Teach Model", "Database Viewer"])

# ---------------- PRODUCT ADVISOR TAB ----------------
with tabs[0]:
    st.header("🛒 Product Advisor")

    product_name = st.text_input("Product Name", key="prod_name")
    product_desc = st.text_area("Product Description", key="prod_desc")
    packaging_type = st.selectbox(
        "Packaging Type",
        ["Primary", "Secondary", "Tertiary"],
        key="pack_type"
    )

    if st.button("Suggest Packaging", key="suggest_btn"):
        if product_name and product_desc:
            st.success(f"✅ Suggested packaging for **{product_name}**:")
            
            # Simple placeholder logic
            if "fragile" in product_desc.lower():
                st.write("🫙 Glass with cushioning + Corrugated box")
            elif "food" in product_desc.lower():
                st.write("🥫 Multilayer laminates or Plastic films")
            else:
                st.write("📦 Standard corrugated fiberboard")
        else:
            st.warning("⚠️ Please enter product details first!")

# ---------------- TEACH MODEL TAB ----------------
with tabs[1]:
    st.header("📚 Teach the Model")

    c_name = st.text_input("Material / Category Name", key="teach_cname")
    c_desc = st.text_area("Description", key="teach_cdesc")
    c_notes = st.text_area("Notes (optional)", key="teach_notes")

    if st.button("Save Category", key="save_category_btn"):
        if c_name:
            db["materials"][c_name] = {
                "description": c_desc,
                "notes": c_notes
            }
            save_db(db)
            st.success(f"✅ Taught model about **{c_name}**")
        else:
            st.warning("⚠️ Please enter a category name!")

    st.subheader("🧠 Teach Mind Map")
    mm_level = st.selectbox(
        "Packaging Level", ["Primary", "Secondary", "Tertiary"], key="teach_level"
    )
    mm_notes = st.text_area("Mind Map Notes", key="teach_mm_notes")

    if st.button("Save Mind Map", key="save_mm_btn"):
        if mm_level:
            db["mindmap"][mm_level] = mm_notes
            save_db(db)
            st.success(f"✅ Saved mind map for {mm_level} packaging")

# ---------------- DATABASE VIEWER TAB ----------------
with tabs[2]:
    st.header("📂 Database Viewer")

    st.json(db, expanded=True)

    st.download_button(
        label="📥 Download Database (JSON)",
        data=json.dumps(db, indent=4),
        file_name="packaging_db.json",
        mime="application/json",
        key="download_db_btn"
    )
