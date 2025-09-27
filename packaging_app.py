
import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "packaging_db.json"

# Load comprehensive database
@st.cache_data
def load_database():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    else:
        return {"products": {}, "packaging_materials": {}, "recommendation_rules": {}, "scoring_parameters": {}}

def save_database(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

def calculate_packaging_score(user_inputs, material_name, material_data, db):
    """Advanced scoring algorithm for packaging compatibility"""
    total_score = 0
    max_possible_score = 0
    scoring_details = []

    scoring_params = db.get("scoring_parameters", {})
    weights = scoring_params.get("compatibility_weights", {})

    # Product State Compatibility (25 points)
    if user_inputs.get('product_state') in material_data['characteristics']['product_state_compatibility']:
        score = weights.get('product_state', 25)
        total_score += score
        scoring_details.append(f"✅ Product state compatibility: +{score}")
    else:
        scoring_details.append("❌ Product state incompatible: +0")
    max_possible_score += weights.get('product_state', 25)

    # Barrier Requirements (20 points)
    barrier_score = 0
    barrier_scoring = scoring_params.get("barrier_scoring", {})

    for barrier_type in ['oxygen', 'moisture', 'light']:
        user_need = user_inputs.get(f'{barrier_type}_sensitivity', 'None')
        material_barrier = material_data['characteristics'][f'{barrier_type}_barrier'].lower()

        if user_need in barrier_scoring.get(barrier_type, {}):
            need_mapping = barrier_scoring[barrier_type][user_need]
            barrier_points = need_mapping.get(material_barrier.title(), 0)
            barrier_score += barrier_points

            if barrier_points > 0:
                scoring_details.append(f"✅ {barrier_type.title()} barrier: +{barrier_points}")
            else:
                scoring_details.append(f"⚠️ {barrier_type.title()} barrier: {barrier_points}")

    total_score += barrier_score
    max_possible_score += weights.get('barrier_requirements', 20)

    # Chemical Compatibility (15 points)
    user_ph = user_inputs.get('ph_level', 'Neutral')
    if user_ph in material_data['characteristics']['ph_tolerance']:
        chem_score = weights.get('chemical_compatibility', 15)
        total_score += chem_score
        scoring_details.append(f"✅ Chemical compatibility: +{chem_score}")
    else:
        scoring_details.append("❌ Chemical incompatibility: +0")
    max_possible_score += weights.get('chemical_compatibility', 15)

    # Cost Alignment (12 points)
    cost_scoring = scoring_params.get("cost_scoring", {})
    user_budget = user_inputs.get('budget_range', 'Standard')
    material_cost = material_data['characteristics']['cost_category']

    if user_budget in cost_scoring and material_cost in cost_scoring[user_budget]:
        cost_score = cost_scoring[user_budget][material_cost]
        total_score += cost_score
        if cost_score > 0:
            scoring_details.append(f"✅ Cost alignment: +{cost_score}")
        else:
            scoring_details.append(f"⚠️ Cost mismatch: {cost_score}")
    max_possible_score += weights.get('cost_alignment', 12)

    # Temperature Requirements (10 points)
    user_temp = user_inputs.get('storage_temperature', 'Ambient')
    if user_temp in material_data['characteristics']['temperature_range']:
        temp_score = weights.get('temperature_requirements', 10)
        total_score += temp_score
        scoring_details.append(f"✅ Temperature compatibility: +{temp_score}")
    else:
        scoring_details.append("❌ Temperature incompatibility: +0")
    max_possible_score += weights.get('temperature_requirements', 10)

    # Sustainability Match (8 points)
    sustain_score = 0
    if user_inputs.get('sustainability_priority') == 'Eco-focused':
        if material_data['sustainability']['recyclable']:
            sustain_score += 4
        if material_data['sustainability']['pcr_available']:
            sustain_score += 2
        if material_data['sustainability']['biodegradable']:
            sustain_score += 2
    else:
        sustain_score = 4  # Neutral score for non-eco focused

    total_score += sustain_score
    max_possible_score += weights.get('sustainability_match', 8)
    scoring_details.append(f"♻️ Sustainability match: +{sustain_score}")

    # Apply recommendation rules bonuses
    rule_bonuses = apply_recommendation_rules(user_inputs, material_name, db)
    total_score += rule_bonuses

    if rule_bonuses > 0:
        scoring_details.append(f"🎯 Rule bonuses: +{rule_bonuses:.1f}")

    final_score = min(100, (total_score / max_possible_score) * 100) if max_possible_score > 0 else 0

    return final_score, scoring_details

def apply_recommendation_rules(user_inputs, material_name, db):
    """Apply intelligent recommendation rules for bonus points"""
    bonus_points = 0
    rules = db.get("recommendation_rules", {})

    for rule_name, rule_data in rules.items():
        rule_triggered = False

        # Check if rule is triggered
        for trigger in rule_data.get("triggers", []):
            for key, value in trigger.items():
                if user_inputs.get(key) == value:
                    rule_triggered = True
                    break

        if rule_triggered:
            if material_name in rule_data.get("recommended_materials", []):
                bonus_points += rule_data.get("priority_score", 0) * 0.3  # 30% of priority as bonus
            elif material_name in rule_data.get("avoid_materials", []):
                bonus_points -= rule_data.get("priority_score", 0) * 0.2  # 20% penalty

    return bonus_points

def get_packaging_recommendations(user_inputs, db):
    """Generate intelligent packaging recommendations"""
    recommendations = []
    materials = db.get("packaging_materials", {})

    for material_name, material_data in materials.items():
        score, details = calculate_packaging_score(user_inputs, material_name, material_data, db)

        recommendations.append({
            'name': material_name.replace('_', ' '),
            'material_name': material_name,
            'score': score,
            'data': material_data,
            'scoring_details': details,
            'reasons': generate_recommendation_reasons(user_inputs, material_data, score)
        })

    # Sort by score (highest first)
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def generate_recommendation_reasons(user_inputs, material_data, score):
    """Generate human-readable explanations for recommendations"""
    reasons = []

    # Product state compatibility
    if user_inputs.get('product_state') in material_data['characteristics']['product_state_compatibility']:
        reasons.append(f"✅ Perfect for {user_inputs.get('product_state').lower()} products")

    # Barrier properties
    barrier_reasons = []
    for barrier_type in ['oxygen', 'moisture', 'light']:
        user_need = user_inputs.get(f'{barrier_type}_sensitivity', 'None')
        material_barrier = material_data['characteristics'][f'{barrier_type}_barrier']

        if user_need == 'High' and material_barrier in ['Excellent', 'High']:
            barrier_reasons.append(f"{barrier_type}")

    if barrier_reasons:
        reasons.append(f"🛡️ Excellent {', '.join(barrier_reasons)} protection")

    # Cost alignment
    if user_inputs.get('budget_range') == material_data['characteristics']['cost_category']:
        reasons.append(f"💰 Matches {user_inputs.get('budget_range').lower()} budget perfectly")

    # Sustainability
    if user_inputs.get('sustainability_priority') == 'Eco-focused':
        sustain_features = []
        if material_data['sustainability']['recyclable']:
            sustain_features.append("recyclable")
        if material_data['sustainability']['pcr_available']:
            sustain_features.append("PCR available")
        if material_data['sustainability']['biodegradable']:
            sustain_features.append("biodegradable")

        if sustain_features:
            reasons.append(f"♻️ Eco-friendly: {', '.join(sustain_features)}")

    # Score-based reasons
    if score >= 90:
        reasons.append("⭐ Exceptional compatibility match")
    elif score >= 75:
        reasons.append("✨ Excellent compatibility")
    elif score >= 60:
        reasons.append("👍 Good compatibility")

    # Technical advantages
    pros = material_data.get('pros', [])[:2]  # Top 2 pros
    for pro in pros:
        reasons.append(f"💪 {pro}")

    return reasons

def main():
    st.set_page_config(
        page_title="🎯 Smart Packaging Advisor Pro",
        page_icon="📦",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Load database
    db = load_database()

    # Header with user name
    st.title("🎯 Smart Packaging Advisor Pro")
    st.markdown('<p style="font-size: 16px; color: #666; margin-top: -10px;">Made by Pushkar Singhania, IIP Delhi, MS Student</p>', unsafe_allow_html=True)
    st.markdown("*AI-Powered Packaging Recommendations Based on Key Parameters*")
    st.markdown("---")

    # Sidebar navigation
    with st.sidebar:
        st.markdown("### 🧭 Navigation")

        page = st.radio("Select Function:", [
            "🎯 Get Smart Recommendations",
            "📋 Browse Products Database", 
            "💾 Save New Product",
            "📊 Material Database",
            "⚙️ System Info"
        ])

        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("Products", len(db.get("products", {})))
        st.metric("Materials", len(db.get("packaging_materials", {})))
        st.metric("Rules", len(db.get("recommendation_rules", {})))

    if page == "🎯 Get Smart Recommendations":
        recommendation_page(db)
    elif page == "📋 Browse Products Database":
        browse_products_page(db)
    elif page == "💾 Save New Product":
        save_product_page(db)
    elif page == "📊 Material Database":
        material_database_page(db)
    else:
        system_info_page(db)

def recommendation_page(db):
    st.header("🎯 Get Smart Packaging Recommendations")
    st.markdown("*Get AI-powered packaging suggestions for your product*")

    # SECTION 1: Product Name
    st.subheader("📝 Step 1: Product Information")

    col1, col2 = st.columns([2, 1])

    with col1:
        product_name = st.text_input(
            "Product Name:", 
            placeholder="e.g., Premium Face Cream, Orange Juice, Vitamin Tablets",
            help="Enter the name of your product"
        )

    with col2:
        if product_name:
            # Check if product exists in database
            products = db.get("products", {})
            if product_name in products:
                st.success(f"✅ Found '{product_name}' in database!")
                if st.button("📋 Load Product Data"):
                    st.session_state.load_product_data = products[product_name]
                    st.success("Product data loaded! Scroll down to see pre-filled details.")

    st.markdown("---")

    # SECTION 2: Essential Product Details (Simplified)
    st.subheader("📋 Step 2: Product Details")
    st.markdown("*Fill out these essential parameters for accurate recommendations*")

    # Check if we should load existing product data
    load_data = st.session_state.get('load_product_data', {})
    rec_profile = load_data.get('recommendation_profile', {})

    # Organize into 2 main tabs instead of 4
    tab1, tab2 = st.tabs(["🔬 Product Characteristics", "🎯 Requirements & Preferences"])

    user_inputs = {}

    with tab1:
        st.markdown("#### Basic Product Properties")

        col1, col2 = st.columns(2)

        with col1:
            user_inputs['product_state'] = st.selectbox(
                "Product State:", 
                ["Liquid", "Solid", "Powder", "Paste", "Semi-solid", "Gas"],
                index=["Liquid", "Solid", "Powder", "Paste", "Semi-solid", "Gas"].index(rec_profile.get('product_state', 'Liquid')),
                help="Physical state of your product"
            )

            user_inputs['viscosity'] = st.selectbox(
                "Viscosity (for liquids):", 
                ["Low", "Medium", "High", "N/A"],
                index=["Low", "Medium", "High", "N/A"].index(rec_profile.get('viscosity', 'N/A')),
                help="Flow characteristics (select N/A for non-liquids)"
            )

            user_inputs['ph_level'] = st.selectbox(
                "pH Level:", 
                ["Acidic", "Neutral", "Basic"],
                index=["Acidic", "Neutral", "Basic"].index(rec_profile.get('ph_level', 'Neutral')),
                help="Chemical nature of your product"
            )

            user_inputs['volume_weight'] = st.text_input(
                "Volume/Weight:", 
                value=load_data.get('properties', {}).get('weight_volume', ''),
                placeholder="e.g., 500ml, 100g, 1kg",
                help="Size/quantity of your product"
            )

        with col2:
            st.markdown("#### Protection Needs")

            user_inputs['oxygen_sensitivity'] = st.selectbox(
                "Oxygen Sensitivity:", 
                ["None", "Low", "Medium", "High"],
                index=["None", "Low", "Medium", "High"].index(rec_profile.get('oxygen_sensitivity', 'None')),
                help="Does oxygen exposure degrade your product?"
            )

            user_inputs['moisture_sensitivity'] = st.selectbox(
                "Moisture Sensitivity:", 
                ["None", "Low", "Medium", "High"],
                index=["None", "Low", "Medium", "High"].index(rec_profile.get('moisture_sensitivity', 'None')),
                help="Does moisture affect product quality?"
            )

            user_inputs['light_sensitivity'] = st.selectbox(
                "Light Sensitivity:", 
                ["None", "Low", "Medium", "High"],
                index=["None", "Low", "Medium", "High"].index(rec_profile.get('light_sensitivity', 'None')),
                help="Does light damage your product?"
            )

            user_inputs['fragility_level'] = st.selectbox(
                "Product Fragility:", 
                ["Robust", "Moderate", "Fragile", "Very Fragile"],
                help="How easily can your product break or get damaged?"
            )

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Storage & Market")

            user_inputs['shelf_life_requirement'] = st.selectbox(
                "Required Shelf Life:", 
                ["Days", "Weeks", "Months", "Years"],
                index=["Days", "Weeks", "Months", "Years"].index(rec_profile.get('shelf_life_requirement', 'Months')),
                help="How long should the product last?"
            )

            user_inputs['storage_temperature'] = st.selectbox(
                "Storage Temperature:", 
                ["Frozen", "Cold", "Cool", "Ambient", "Hot"],
                index=["Frozen", "Cold", "Cool", "Ambient", "Hot"].index(rec_profile.get('storage_temperature', 'Ambient')),
                help="Required storage conditions"
            )

            user_inputs['target_market'] = st.selectbox(
                "Target Market:", 
                ["Consumer retail", "Professional", "Industrial", "Medical"],
                help="Who will use this product?"
            )

            user_inputs['industry_category'] = st.selectbox(
                "Industry Type:", 
                ["Food", "Pharma", "Cosmetic", "Chemical", "Electronics", "Industrial"],
                index=["Food", "Pharma", "Cosmetic", "Chemical", "Electronics", "Industrial"].index(load_data.get('basic_info', {}).get('category', 'Food')),
                help="What industry is this for?"
            )

        with col2:
            st.markdown("#### Budget & Preferences")

            user_inputs['budget_range'] = st.selectbox(
                "Budget Range:", 
                ["Economy", "Standard", "Premium"],
                index=["Economy", "Standard", "Premium"].index(rec_profile.get('budget_range', 'Standard')),
                help="What's your packaging budget level?"
            )

            user_inputs['sustainability_priority'] = st.selectbox(
                "Sustainability Priority:", 
                ["Cost focused", "Balanced", "Eco-focused"],
                index=["Cost focused", "Balanced", "Eco-focused"].index(rec_profile.get('sustainability_priority', 'Balanced')),
                help="How important is environmental impact?"
            )

            user_inputs['safety_requirements'] = st.multiselect(
                "Safety Features Needed:", 
                ["Child resistant", "Tamper evident", "Sterile", "Anti-static", "Hazmat"],
                help="Special safety features required"
            )

            user_inputs['brand_positioning'] = st.selectbox(
                "Brand Positioning:", 
                ["Value", "Mainstream", "Premium", "Luxury"],
                help="How is your brand positioned?"
            )

    # Clear loaded data after use
    if 'load_product_data' in st.session_state:
        del st.session_state.load_product_data

    st.markdown("---")

    # Generate recommendations button
    if st.button("🎯 Generate Smart Recommendations", type="primary", use_container_width=True):
        if not product_name:
            st.error("❌ Please enter a product name first!")
            return

        with st.spinner("🤖 AI is analyzing your requirements..."):
            recommendations = get_packaging_recommendations(user_inputs, db)

        st.success(f"🎉 Here are the packaging recommendations for **{product_name}**!")

        # Display top 5 recommendations
        for i, rec in enumerate(recommendations[:5], 1):
            score_color = "green" if rec['score'] >= 75 else "orange" if rec['score'] >= 50 else "red"

            with st.expander(f"#{i} {rec['name']} - {rec['score']:.1f}% Match", expanded=i<=3):
                col_info, col_details, col_reasons = st.columns([1, 1, 1])

                with col_info:
                    st.markdown(f"**Score: :{score_color}[{rec['score']:.1f}%]**")
                    st.write(f"**Type:** {rec['data']['material_type']}")
                    st.write(f"**Cost:** {rec['data']['characteristics']['cost_category']}")

                    # Barrier properties
                    barriers = []
                    for barrier_type in ['oxygen', 'moisture', 'light']:
                        level = rec['data']['characteristics'][f'{barrier_type}_barrier']
                        barriers.append(f"{barrier_type.title()}: {level}")
                    st.write(f"**Barriers:** {', '.join(barriers)}")

                with col_details:
                    st.write("**Detailed Scoring:**")
                    for detail in rec['scoring_details'][:5]:  # Show top 5 scoring details
                        st.write(f"• {detail}")

                with col_reasons:
                    st.write("**Why This Packaging:**")
                    for reason in rec['reasons']:
                        st.write(f"• {reason}")

                # Technical details expandable
                with st.expander("🔬 Technical Specifications"):
                    tech_specs = rec['data'].get('technical_specs', {})
                    for key, value in tech_specs.items():
                        st.write(f"**{key.replace('_', ' ').title()}:** {value}")

                # Pros and cons
                col_pros, col_cons = st.columns(2)
                with col_pros:
                    st.write("**✅ Advantages:**")
                    for pro in rec['data'].get('pros', []):
                        st.write(f"• {pro}")

                with col_cons:
                    st.write("**⚠️ Considerations:**")
                    for con in rec['data'].get('cons', []):
                        st.write(f"• {con}")

        # FIXED: Add final packaging recommendations summary
        st.markdown("---")
        st.subheader(f"📦 Final Recommendations for {product_name}")

        top_3 = recommendations[:3]

        col1, col2, col3 = st.columns(3)

        for i, rec in enumerate(top_3):
            with [col1, col2, col3][i]:
                score_color = "🟢" if rec['score'] >= 75 else "🟡" if rec['score'] >= 50 else "🔴"
                st.markdown(f"### {score_color} #{i+1} {rec['name']}")
                st.markdown(f"**{rec['score']:.1f}% Match**")
                st.write(f"**Type:** {rec['data']['material_type']}")
                st.write(f"**Cost:** {rec['data']['characteristics']['cost_category']}")

                # Top 2 reasons
                st.write("**Key Benefits:**")
                for reason in rec['reasons'][:2]:
                    st.write(f"• {reason}")

def browse_products_page(db):
    st.header("📋 Browse Products Database")

    products = db.get("products", {})

    if not products:
        st.warning("No products found in database.")
        return

    # Search and filter
    col1, col2 = st.columns([2, 1])

    with col1:
        search_term = st.text_input("🔍 Search Products:", placeholder="Type product name...")

    with col2:
        categories = set()
        for product_data in products.values():
            if product_data.get("basic_info", {}).get("category"):
                categories.add(product_data["basic_info"]["category"])
        categories = sorted(list(categories))
        category_filter = st.selectbox("📂 Filter by Category:", ["All Categories"] + categories)

    # Filter products
    filtered_products = []
    for product_name, product_data in products.items():
        product_category = product_data.get("basic_info", {}).get("category", "")

        search_match = True
        if search_term:
            search_match = search_term.lower() in product_name.lower()

        category_match = True
        if category_filter != "All Categories":
            category_match = product_category == category_filter

        if search_match and category_match:
            filtered_products.append((product_name, product_data))

    st.info(f"📊 Found {len(filtered_products)} products")

    # Display products
    for product_name, product_data in filtered_products:
        with st.expander(f"📦 {product_name}"):
            col1, col2 = st.columns(2)

            with col1:
                basic_info = product_data.get("basic_info", {})
                st.write(f"**Category:** {basic_info.get('category', 'N/A')}")
                st.write(f"**Subcategory:** {basic_info.get('subcategory', 'N/A')}")
                st.write(f"**Market:** {basic_info.get('intended_market', 'N/A')}")

                properties = product_data.get("properties", {})
                st.write(f"**Volume/Weight:** {properties.get('weight_volume', 'N/A')}")
                st.write(f"**Shelf Life:** {properties.get('shelf_life', 'N/A')}")

            with col2:
                packaging = product_data.get("packaging", {})
                st.write("**Packaging Solutions:**")
                st.write(f"• Primary: {', '.join(packaging.get('primary', []))}")
                st.write(f"• Secondary: {', '.join(packaging.get('secondary', []))}")
                st.write(f"• Tertiary: {', '.join(packaging.get('tertiary', []))}")

def save_product_page(db):
    st.header("💾 Save New Product")
    st.markdown("*Add a new product to the database with comprehensive details*")

    product_name = st.text_input("Product Name:", placeholder="e.g., Premium Face Serum")

    if product_name:
        if product_name in db.get("products", {}):
            st.error(f"Product '{product_name}' already exists!")
            return

        # Basic Information
        st.subheader("Basic Information")
        col1, col2, col3 = st.columns(3)

        with col1:
            category = st.selectbox("Category:", ["Food", "Pharma", "Cosmetic", "Chemical", "Electronics", "Industrial", "Pet Care", "Home Care"])

        with col2:
            subcategory = st.text_input("Subcategory:", placeholder="e.g., Skincare")

        with col3:
            market = st.selectbox("Intended Market:", ["Retail", "Professional", "Industrial", "Medical"])

        # Properties
        st.subheader("Product Properties")
        col1, col2 = st.columns(2)

        with col1:
            weight_volume = st.text_input("Weight/Volume:", placeholder="e.g., 30ml")
            shape_form = st.text_input("Shape/Form:", placeholder="e.g., Viscous liquid")
            shelf_life = st.selectbox("Shelf Life:", ["Short-term", "Medium-term", "Long-term"])

        with col2:
            fragility = st.selectbox("Fragility:", ["Low", "Medium", "High"])
            moisture_sensitivity = st.selectbox("Moisture Sensitivity:", ["Yes", "No"])
            light_sensitivity = st.selectbox("Light Sensitivity:", ["Yes", "No"])

        # Packaging Solutions
        st.subheader("Packaging Solutions")
        primary = st.text_area("Primary Packaging (comma-separated):", placeholder="e.g., Glass Bottle, Pump Dispenser")
        secondary = st.text_area("Secondary Packaging (comma-separated):", placeholder="e.g., Carton Box")
        tertiary = st.text_area("Tertiary Packaging (comma-separated):", placeholder="e.g., Shipping Case")

        if st.button("💾 Save Product", type="primary"):
            new_product = {
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
                    "moisture_sensitivity": moisture_sensitivity,
                    "light_sensitivity": light_sensitivity
                },
                "packaging": {
                    "primary": [p.strip() for p in primary.split(",") if p.strip()],
                    "secondary": [s.strip() for s in secondary.split(",") if s.strip()],
                    "tertiary": [t.strip() for t in tertiary.split(",") if t.strip()]
                },
                "created_date": datetime.now().isoformat()
            }

            db["products"][product_name] = new_product
            save_database(db)
            st.success(f"✅ Product '{product_name}' saved successfully!")
            st.rerun()

def material_database_page(db):
    st.header("📊 Packaging Materials Database")

    materials = db.get("packaging_materials", {})

    if not materials:
        st.warning("No materials found in database.")
        return

    # Material overview
    st.subheader("📈 Database Overview")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Materials", len(materials))

    with col2:
        recyclable_count = sum(1 for m in materials.values() if m['sustainability']['recyclable'])
        st.metric("Recyclable Materials", recyclable_count)

    with col3:
        cost_categories = [m['characteristics']['cost_category'] for m in materials.values()]
        premium_count = cost_categories.count('Premium')
        st.metric("Premium Materials", premium_count)

    # Material details
    for material_name, material_data in materials.items():
        with st.expander(f"📦 {material_name.replace('_', ' ')}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Basic Properties:**")
                chars = material_data['characteristics']
                st.write(f"• Type: {material_data['material_type']}")
                st.write(f"• Cost Category: {chars['cost_category']}")
                st.write(f"• Product States: {', '.join(chars['product_state_compatibility'])}")

            with col2:
                st.write("**Barrier Properties:**")
                st.write(f"• Oxygen: {chars['oxygen_barrier']}")
                st.write(f"• Moisture: {chars['moisture_barrier']}")
                st.write(f"• Light: {chars['light_barrier']}")
                st.write(f"• Chemical Resistance: {chars['chemical_resistance']}")

            with col3:
                st.write("**Sustainability:**")
                sust = material_data['sustainability']
                st.write(f"• Recyclable: {'✅' if sust['recyclable'] else '❌'}")
                st.write(f"• PCR Available: {'✅' if sust['pcr_available'] else '❌'}")
                st.write(f"• Biodegradable: {'✅' if sust['biodegradable'] else '❌'}")

            # Technical specs
            if 'technical_specs' in material_data:
                st.write("**Technical Specifications:**")
                tech_cols = st.columns(2)
                specs = material_data['technical_specs']

                for i, (key, value) in enumerate(specs.items()):
                    with tech_cols[i % 2]:
                        st.write(f"• {key.replace('_', ' ').title()}: {value}")

def system_info_page(db):
    st.header("⚙️ System Information")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Database Statistics")
        st.write(f"**Products:** {len(db.get('products', {}))}")
        st.write(f"**Packaging Materials:** {len(db.get('packaging_materials', {}))}")
        st.write(f"**Recommendation Rules:** {len(db.get('recommendation_rules', {}))}")

        # Database size
        import sys
        db_size = sys.getsizeof(str(db)) / 1024  # KB
        st.write(f"**Database Size:** {db_size:.1f} KB")

    with col2:
        st.subheader("🎯 System Features")
        st.write("✅ AI-Powered Recommendations")
        st.write("✅ Simplified Parameter Input")
        st.write("✅ Advanced Scoring Algorithm")
        st.write("✅ Technical Material Database")
        st.write("✅ Sustainability Analysis")
        st.write("✅ Cost Optimization")
        st.write("✅ Real-time Product Search")

    st.subheader("🏗️ System Architecture")
    st.write("""
    **Smart Packaging Advisor Pro** uses:
    - **Intelligent Scoring**: Multi-parameter compatibility analysis
    - **Rule Engine**: Context-aware recommendations
    - **Material Database**: Comprehensive packaging materials library  
    - **Sustainability Metrics**: Environmental impact assessment
    - **Technical Specifications**: Detailed material properties
    """)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    🚀 <b>Smart Packaging Advisor Pro</b> by Pushkar Singhania | IIP Delhi<br>
    Advanced Packaging Engineering & Materials Science
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
