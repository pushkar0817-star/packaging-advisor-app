import streamlit as st
import json

# Load database
with open("packaging_db.json", "r") as f:
    packaging_db = json.load(f)

st.title("📦 Packaging Advisor App")

# Step 1: Ask category
category = st.selectbox("Select Product Category", list(packaging_db["categories"].keys()), key="category")

# Step 2: Ask subcategory
subcategory = st.selectbox(
    "Select Subcategory", 
    list(packaging_db["categories"][category]["subcategories"].keys()), 
    key="subcategory"
)

# Step 3: Fetch data
packaging_info = packaging_db["categories"][category]["subcategories"][subcategory]

st.subheader("🔍 Product Information")
st.write("**Examples:**", ", ".join(packaging_info["examples"]))
st.write("**Properties:**")
for k, v in packaging_info["properties"].items():
    st.write(f"- {k.capitalize()}: {v}")

st.subheader("📦 Recommended Packaging")
st.write("**Primary:**", ", ".join(packaging_info["packaging"]["primary"]))
st.write("**Secondary:**", ", ".join(packaging_info["packaging"]["secondary"]))
st.write("**Tertiary:**", ", ".join(packaging_info["packaging"]["tertiary"]))

# Optional notes
notes = st.text_area("📝 Special Requirements / Notes (optional)", key="notes")

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:gray;'>Created by Pushkar Singhania | IIP Delhi</p>",
    unsafe_allow_html=True
)
