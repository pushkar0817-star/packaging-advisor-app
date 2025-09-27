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

# Step 1: Enhanced Product Search & Category Selection
st.subheader("🔍 Find or Add Product")

# Get existing products and categories
existing_products = list(packaging_db["products"].keys())
categories = set()
for product_data in packaging_db["products"].values():
    if product_data.get("basic_info", {}).get("category"):
        categories.add(product_data["basic_info"]["category"])
categories = sorted(list(categories))

# Create two columns for search and category filter
col1, col2 = st.columns([2, 1])

with col1:
    search_term = st.text_input("🔍 Search Products:", placeholder="Type product name to search...", key="search_box")

with col2:
    category_filter = st.selectbox("📂 Filter by Category:", ["All Categories"] + categories, key="category_filter")

# Filter products based on search and category
filtered_products = []
if existing_products:
    for product in existing_products:
        product_data = packaging_db["products"][product]
        product_category = product_data.get("basic_info", {}).get("category", "")
        
        # Apply search filter
        search_match = True
        if search_term:
            search_match = search_term.lower() in product.lower()
        
        # Apply category filter
        category_match = True
        if category_filter != "All Categories":
            category_match = product_category == category_filter
        
        if search_match and category_match:
            filtered_products.append(product)

# Display search results
if search_term or category_filter != "All Categories":
    if filtered_products:
        st.success(f"📋 Found {len(filtered_products)} product(s):")
        
        # Display filtered products as clickable buttons
        cols = st.columns(min(3, len(filtered_products)))
        selected_product = None
        
        for i, product in enumerate(filtered_products):
            product_data = packaging_db["products"][product]
            category = product_data.get("basic_info", {}).get("category", "Unknown")
            
            with cols[i % 3]:
                if st.button(f"📦 **{product}**\n*({category})*", key=f"select_{product}", use_container_width=True):
                    selected_product = product
        
        # Set product_name if a product was selected
        if selected_product:
            st.session_state.selected_product = selected_product
    else:
        st.warning("❌ No products found matching your criteria")

# Handle product selection or new product entry
product_name = ""
if 'selected_product' in st.session_state and st.session_state.selected_product:
    product_name = st.session_state.selected_product
    st.info(f"✅ **Selected: {product_name}**")
    if st.button("🔄 Clear Selection", key="clear_selection"):
        del st.session_state.selected_product
        st.rerun()

# Option to add new product
st.markdown("---")
st.subheader("➕ Add New Product")
new_product_name = st.text_input("Enter New Product Name:", placeholder="e.g., Orange Juice, Face Cream", key="new_product_input")

if new_product_name:
    if new_product_name in existing_products:
        st.error(f"⚠️ '{new_product_name}' already exists! Use search above to find it.")
    else:
        if st.button(f"✅ Create '{new_product_name}'", key="create_new"):
            product_name = new_product_name
            st.session_state.new_product_created = True

# Only proceed if we have a product name
if product_name:
    st.markdown("---")
    
    if product_name in packaging_db["products"]:
        product_info = packaging_db["products"][product_name]
        st.info(f"📋 **Editing existing product:** {product_name}")
    else:
        st.success(f"🆕 **Creating new product:** {product_name}")
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
        
        # Clear session state after saving
        if 'selected_product' in st.session_state:
            del st.session_state.selected_product
        st.rerun()
    
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
