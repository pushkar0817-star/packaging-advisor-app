import json, os
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---- Force Streamlit to clear old cached layouts ----
st.cache_data.clear()

# ---- Load database ----
def load_database():
    try:
        with open("data.json", "r") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"❌ Could not load data.json — {e}")
        return {}

db = load_database()

# ---- Recommendation logic ----
def recommend_materials(product_name, db):
    products = db.get("products", {})
    materials = db.get("packaging_materials", {})
    rules = db.get("recommendation_rules", {})

    if product_name not in products:
        return []

    product_desc = products[product_name].get("description", "")
    matched_materials = []

    # Rule-based
    for rule in rules.values():
        trig = rule.get("trigger", "").lower()
        if trig and (trig in product_name.lower() or trig in product_desc.lower()):
            matched_materials.extend(rule.get("materials", []))

    # TF-IDF fallback
    if not matched_materials and materials:
        mat_names = list(materials.keys())
        mat_descs = [materials[m].get("description", "") for m in mat_names]
        vectorizer = TfidfVectorizer()
        tfidf = vectorizer.fit_transform([product_desc] + mat_descs)
        sims = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        top = sims.argsort()[-3:][::-1]
        matched_materials = [mat_names[i] for i in top]

    recs = []
    for m in matched_materials:
        if m in materials:
            info = materials[m]
            recs.append({
                "Material": m,
                "Description": info.get("description", "N/A"),
                "Cost": info.get("cost", "N/A"),
                "Barrier Strength": info.get("barrier_strength", "N/A"),
                "Sustainability": info.get("sustainability", "N/A"),
            })
    return recs

# ---- Streamlit UI ----
st.set_page_config(page_title="Packaging Chat", page_icon="📦", layout="centered")

st.markdown("<h1 style='text-align:center;'>🤖 Packaging Advisory Chat</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Type your product name below and get instant packaging recommendations.</p>", unsafe_allow_html=True)

# Single input only
product_name = st.text_input("💬 What is your product name?", placeholder="e.g., Milk, Shampoo, Chips...")

if st.button("Get Recommendations 🚀", use_container_width=True):
    if not product_name.strip():
        st.warning("Please enter a product name.")
    else:
        recs = recommend_materials(product_name.strip(), db)
        if not recs:
            st.info("No matches found. Try a different name or check data.json.")
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

st.caption("💡 Uses your existing `data.json`. No API key required.")
