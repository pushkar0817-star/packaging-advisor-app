import json
import streamlit as st
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------- LOAD DATABASE ----------
@st.cache_data
def load_database():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("❌ data.json not found in the same folder!")
        return {}

db = load_database()

# ---------- RECOMMENDATION LOGIC ----------
def recommend_materials(product_name, db):
    if "products" not in db or "packaging_materials" not in db:
        return []

    products = db["products"]
    materials = db["packaging_materials"]

    if product_name not in products:
        return []

    product_data = products[product_name]
    product_desc = product_data.get("description", "")
    rules = db.get("recommendation_rules", {})

    # Step 1: Try to match rules for this product
    matched_materials = []
    for rule_name, rule in rules.items():
        trigger = rule.get("trigger", "").lower()
        if trigger in product_name.lower() or trigger in product_desc.lower():
            matched_materials.extend(rule.get("materials", []))

    # Step 2: TF-IDF fallback if no rules match
    if not matched_materials:
        material_names = list(materials.keys())
        material_descs = [materials[m].get("description", "") for m in material_names]
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([product_desc] + material_descs)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        top_indices = sims.argsort()[-3:][::-1]
        matched_materials = [material_names[i] for i in top_indices]

    # Step 3: Gather material data
    recommendations = []
    for mat in matched_materials:
        if mat in materials:
            recommendations.append({
                "Material": mat,
                "Description": materials[mat].get("description", "No description available"),
                "Cost": materials[mat].get("cost", "N/A"),
                "Barrier Strength": materials[mat].get("barrier_strength", "N/A"),
                "Sustainability": materials[mat].get("sustainability", "N/A"),
            })
    return recommendations


# ---------- STREAMLIT APP ----------
st.set_page_config(page_title="Packaging Advisory App", page_icon="📦", layout="centered")

st.title("🤖 Packaging Advisory Chat")
st.markdown("Ask me about your **product**, and I’ll recommend the best packaging materials!")

# Chat-like input
product_name = st.text_input("💬 What is your product name?", placeholder="e.g., Milk, Shampoo, Chips...")

if st.button("Get Packaging Recommendations 🚀"):
    if not product_name:
        st.warning("Please enter a product name first.")
    else:
        recs = recommend_materials(product_name.strip(), db)
        if not recs:
            st.info("No direct matches found. Try another product name or check your database.")
        else:
            st.success(f"Top Packaging Recommendations for **{product_name}**:")
            for r in recs:
                with st.container():
                    st.markdown(f"### 🧱 {r['Material']}")
                    st.write(f"**Description:** {r['Description']}")
                    st.write(f"**Barrier Strength:** {r['Barrier Strength']}")
                    st.write(f"**Sustainability:** {r['Sustainability']}")
                    st.write(f"**Cost:** {r['Cost']}")
                    st.markdown("---")

st.caption("💡 Works fully offline with your existing `data.json`. AI features optional.")
