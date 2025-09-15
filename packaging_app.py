import json
import streamlit as st

# Load knowledge database
def load_db():
    try:
        with open("packaging_db.json", "r") as f:
            return json.load(f)
    except:
        return {}

db = load_db()

# Main UI
st.title("🛒 Product Advisor")

col1, col2 = st.columns(2)
with col1:
    product_name = st.text_input("✏️ Product Name").lower()
with col2:
    packaging_type = st.selectbox("📦 Packaging Type", ["Primary", "Secondary", "Tertiary"])

product_desc = st.text_area("📝 Product Description")

if st.button("🚀 Suggest Packaging"):
    suggestion = None

    # 1. Try exact match from DB
    if product_name in db:
        if packaging_type in db[product_name]:
            suggestion = db[product_name][packaging_type]

    # 2. If not taught, fallback rules
    if not suggestion:
        if "fruit" in product_desc or "apple" in product_name:
            if packaging_type == "Primary":
                suggestion = "Plastic tray with shrink wrap 🍎"
            elif packaging_type == "Secondary":
                suggestion = "Corrugated box with partitions 📦"
            else:
                suggestion = "Palletized corrugated cartons with stretch film 🚚"
        elif "bottle" in product_desc or "liquid" in product_desc:
            if packaging_type == "Primary":
                suggestion = "Glass/Plastic bottle with cap 🍼"
            elif packaging_type == "Secondary":
                suggestion = "Carton for 6/12 bottles 📦"
            else:
                suggestion = "Pallet wrap with shrink film 🚚"
        else:
            suggestion = f"No trained data. Please teach me for {packaging_type} packaging 🤖"

    # Display suggestion
    st.success(f"Suggested {packaging_type} packaging for **{product_name}** → {suggestion}")
