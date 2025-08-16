import streamlit as st
import json
import os
import time

# File where knowledge will be stored
DB_FILE = "packaging_db.json"

# Load existing knowledge
def load_knowledge():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# Save knowledge to file
def save_knowledge(knowledge):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(knowledge, f, indent=4, ensure_ascii=False)

# Initialize knowledge base
if "knowledge_base" not in st.session_state:
    st.session_state.knowledge_base = load_knowledge()

# 🎨 Fancy Title with animation
st.markdown(
    "<h1 style='text-align: center; color: #FF6F61;'>✨📦 AI Packaging Advisor with Memory ✨</h1>",
    unsafe_allow_html=True
)

# ================= MAIN PAGE =================
st.subheader("📝 Product Input")

product_name = st.text_input("💡 Enter your Product Name")
product_desc = st.text_area("🧾 Enter Product Description")
packaging_type = st.selectbox(
    "📦 Select Packaging Type",
    ["Transportation 🚚", "Storage 📦", "Retail 🛍️", "Export 🌍"]
)

# --- Auto Categorize ---
def categorize_product(description):
    desc = description.lower()
    if any(word in desc for word in ["food", "snack", "beverage", "drink", "fruit", "vegetable"]):
        return "🥗 Food & Beverages"
    elif any(word in desc for word in ["mobile", "electronics", "gadget", "laptop", "device"]):
        return "📱 Electronics"
    elif any(word in desc for word in ["bottle", "liquid", "oil", "juice", "shampoo"]):
        return "🧴 Liquids"
    elif any(word in desc for word in ["glass", "ceramic", "fragile", "delicate"]):
        return "🍷 Fragile Items"
    elif any(word in desc for word in ["metal", "tools", "hardware", "machine"]):
        return "⚙️ Industrial Goods"
    else:
        return "📦 General Products"

if product_desc:
    category = categorize_product(product_desc)
    st.success(f"🔍 Auto-detected category: **{category}**")
else:
    category = None

# --- Suggest Packaging ---
if st.button("🚀 Suggest Packaging"):
    if not product_name or not product_desc:
        st.error("⚠️ Please enter both product name and description.")
    else:
        # 🎉 Fun animation
        st.balloons()
        with st.spinner("Thinking 🤔..."):
            time.sleep(2)

        st.subheader("📌 Suggested Packaging:")
        st.write(f"**🛒 Product Category:** {category}")
        st.write(f"**📦 Packaging Type Chosen:** {packaging_type}")

        if st.session_state.knowledge_base:
            for material, details in st.session_state.knowledge_base.items():
                st.markdown(f"- 🎁 **{material}** → {details}")
        else:
            st.info("🤖 I don’t know any packaging materials yet. Please teach me first!")

# ================= SIDEBAR =================
st.sidebar.header("🧑‍🏫 Teach the System")

new_material = st.sidebar.text_input("✨ Packaging Material Name (e.g., Multilayer Laminate, Corrugated Board)")
new_details = st.sidebar.text_area("📘 Define Properties & Best Use Cases")

if st.sidebar.button("💾 Teach"):
    if new_material and new_details:
        st.session_state.knowledge_base[new_material] = new_details
        save_knowledge(st.session_state.knowledge_base)
        st.sidebar.success(f"✅ Taught system about: {new_material}")
        st.sidebar.snow()
    else:
        st.sidebar.warning("⚠️ Please provide both material name and details.")

# --- 📂 View Database Section ---
st.sidebar.header("📂 My Packaging Knowledge Base")

if st.session_state.knowledge_base:
    for material, details in st.session_state.knowledge_base.items():
        with st.sidebar.expander(f"🎁 {material}"):
            st.write(details)

    # 👀 JSON Viewer
    st.sidebar.subheader("🔎 Full Database (JSON Viewer)")
    st.sidebar.json(st.session_state.knowledge_base)

    # ⬇️ Download Button
    st.sidebar.download_button(
        label="⬇️ Download Database Backup",
        data=json.dumps(st.session_state.knowledge_base, indent=4, ensure_ascii=False),
        file_name="packaging_db_backup.json",
        mime="application/json"
    )
else:
    st.sidebar.info("📭 No packaging materials taught yet.")
