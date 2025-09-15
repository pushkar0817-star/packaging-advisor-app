import streamlit as st
import json
import os

DB_FILE = "packaging_db.json"

# Load database
if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f:
        packaging_db = json.load(f)
else:
    packaging_db = {"products": {}}

st.title("📦 Packaging Advisor App")

# Step 1: Ask product name
product_name = st.text_input("Enter Product Name (e.g., Milk, Tablet)", key="product_name")

if product_name:
    if product_name in packaging_db["products"]:
        product_info = packaging_db["products"][product_name]
    else:
        st.warning(f"'{product_name}' not found. Fill details below to add it to the database.")
        # Create an empty template if new
        product_info = {
            "basic_info": {"category": "", "subcategory": "", "intended_market": ""},
            "properties": {},
            "handling": {},
            "consumer": {},
            "regulatory": {},
            "packaging": {"primary": [], "secondary": [], "tertiary": []}
        }

    st.subheader("✏️ Product Description")

    # Basic Info
    category = st.text_input("Category", value=product_info["basic_info"].get("category", ""))
    subcategory = st.text_input("Subcategory", value=product_info["basic_info"].get("subcategory", ""))
    market = st.text_input("Intended Market", value=product_info["basic_info"].get("intended_market", ""))

    # Properties
    weight_volume = st.text_input("Weight / Volume", value=product_info["properties"].get("weight_volume", ""))
    shape_form = st.text_input("Shape / Form", value=product_info["properties"].get("shape_form", ""))
    shelf_life = st.selectbox("Shelf Life", ["Short-term", "Medium-term", "Long-term"],
                              index=["Short-term", "Medium-term", "Long-term"].index(
                                  product_info["properties"].get("shelf_life", "Medium-term")))
    fragility = st.selectbox("Fragility", ["Low", "Medium", "High"],
                             index=["Low", "Medium", "High"].index(
                                 product_info["properties"].get("fragility", "Low")))
    moisture = st.selectbox("Moisture Sensitivity", ["Yes", "No"],
                            index=["Yes", "No"].index(product_info["properties"].get("moisture_sensitivity", "No")))
    light = st.selectbox("Light Sensitivity", ["Yes", "No"],
                         index=["Yes", "No"].index(product_info["properties"].get("light_sensitivity", "No")))

    # Handling
    distribution = st.text_input("Mode of Distribution", value=product_info["handling"].get("mode_distribution", ""))
    transport = st.text_input("Transport Conditions", value=product_info["handling"].get("transport_conditions", ""))

    # Consumer
    target_consumer = st.text_input("Target Consumer", value=product_info["consumer"].get("target_consumer", ""))
    branding = st.text_input("Branding / Printing", value=product_info["consumer"].get("branding_printing", ""))

    # Regulatory
    compliance = st.text_area("Compliance Requirements (comma-separated)",
                              value=", ".join(product_info["regulatory"].get("compliance", [])))
    sustainability = st.text_area("Sustainability Requirements (comma-separated)",
                                  value=", ".join(product_info["regulatory"].get("sustainability", [])))

    # Packaging
    primary = st.text_area("Primary Packaging (comma-separated)", 
                           value=", ".join(product_info["packaging"].get("primary", [])))
    secondary = st.text_area("Secondary Packaging (comma-separated)", 
                             value=", ".join(product_info["packaging"].get("secondary", [])))
    tertiary = st.text_area("Tertiary Packaging (comma-separated)", 
                            value=", ".join(product_info["packaging"].get("tertiary", [])))

    # Save button
    if st.button("💾 Save Product to Database"):
        # Update database entry
        packaging_db["products"][product_name] = {
            "basic_info": {
                "category": category,
                "subcategory": subcategory,
                "intended_market": market
            },
            "properties": {
                "weight_volume": weight_volume,
                "shape_form": shape_form,
                "shelf_life": shelf_life,
                "fragility": fragility,
                "moisture_sensitivity": moisture,
                "light_sensitivity": light
            },
            "handling": {
                "mode_distribution": distribution,
                "transport_conditions": transport
            },
            "consumer": {
                "target_consumer": target_consumer,
                "branding_printing": branding
            },
            "regulatory": {
                "compliance": [c.strip() for c in compliance.split(",") if c.strip()],
                "sustainability": [s.strip() for s in sustainability.split(",") if s.strip()]
            },
            "packaging": {
                "primary": [p.strip() for p in primary.split(",") if p.strip()],
                "secondary": [s.strip() for s in secondary.split(",") if s.strip()],
                "tertiary": [t.strip() for t in tertiary.split(",") if t.strip()]
            }
        }

        # Save to file
        with open(DB_FILE, "w") as f:
            json.dump(packaging_db, f, indent=2)

        st.success(f"✅ '{product_name}' saved to database!")

    # Show final packaging recommendation
    st.subheader("📦 Recommended Packaging")
    st.write("**Primary:**", ", ".join(product_info["packaging"].get("primary", [])))
    st.write("**Secondary:**", ", ".join(product_info["packaging"].get("secondary", [])))
    st.write("**Tertiary:**", ", ".join(product_info["packaging"].get("tertiary", [])))

# Footer
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    "<p style='text-align:center; color:gray;'>Created by Pushkar Singhania | IIP Delhi</p>",
    unsafe_allow_html=True
)
