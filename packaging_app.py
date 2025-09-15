import streamlit as st
import json
import os

DB_FILE = "packaging_db.json"

# -----------------
# Load / Save DB
# -----------------
def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        return {"products": {}}

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

data = load_db()

# -----------------
# Streamlit UI
# -----------------
st.set_page_config(page_title="Packaging Advisor", layout="wide")

st.title("📦 Packaging Advisor AI")
st.markdown("Your assistant for **Primary, Secondary, and Tertiary Packaging** suggestions.")

# Tabs for functionality
tab1, tab2, tab3 = st.tabs(["🔍 Suggest Packaging", "🧑‍🏫 Teach Model", "📂 View Database"])

# -----------------
# Suggest Packaging Tab
# -----------------
with tab1:
    st.subheader("Suggest Packaging for a Product")

    product_name = st.text_input("Enter Product Name (e.g., Milk, Tablet, Shampoo)").strip().title()

    if product_name:
        if product_name in data["products"]:
            details = data["products"][product_name]

            st.success(f"✅ Found data for **{product_name}**")

            st.write("### Product Info")
            st.json(details["basic_info"])

            st.write("### Packaging Recommendation")
            st.write(f"**Primary Packaging:** {', '.join(details['packaging']['primary'])} 🥤")
            st.write(f"**Secondary Packaging:** {', '.join(details['packaging']['secondary'])} 📦")
