
import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "packaging_db.json"

# Load database
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

def get_search_suggestions(query, db, max_suggestions=5):
    """Get search suggestions based on user input"""
    if not query or len(query) < 1:
        return []

    query_lower = query.lower()
    suggestions = []

    # Get all product names from database
    products = db.get("products", {})
    product_names = list(products.keys())

    # Add common food products that might not be in database
    common_foods = [
        "Apple Juice", "Banana", "Butter", "Cheese", "Chicken", "Cookies", 
        "Crackers", "Eggs", "Fish", "Flour", "Jam", "Ketchup", "Lemon", 
        "Meat", "Noodles", "Onion", "Pepper", "Salt", "Sugar", "Tea", 
        "Tomato", "Vinegar", "Wine", "Biscuits", "Cake", "Candy", 
        "Ice Cream", "Nuts", "Pickles", "Sauce", "Spices", "Vegetables",
        "Fruit Juice", "Energy Drink", "Soda", "Water Bottle", "Sports Drink",
        "Protein Powder", "Granola Bars", "Trail Mix", "Dried Fruits"
    ]

    all_products = product_names + common_foods

    # Find matches
    for product in all_products:
        if query_lower in product.lower():
            # Prioritize exact matches and database products
            priority = 0
            if product in product_names:
                priority += 10  # Database products get higher priority
            if product.lower().startswith(query_lower):
                priority += 5   # Starting matches get higher priority
            if product.lower() == query_lower:
                priority += 20  # Exact matches get highest priority

            suggestions.append((product, priority))

    # Sort by priority and return top suggestions
    suggestions.sort(key=lambda x: x[1], reverse=True)
    return [suggestion[0] for suggestion in suggestions[:max_suggestions]]

def display_search_suggestions(suggestions, query):
    """Display search suggestions in a nice format"""
    if not suggestions:
        return None

    st.markdown("**💡 Suggestions:**")

    # Create columns for suggestions
    if len(suggestions) <= 3:
        cols = st.columns(len(suggestions))
    else:
        cols = st.columns(3)

    selected_suggestion = None

    for i, suggestion in enumerate(suggestions[:6]):  # Show max 6 suggestions
        col_index = i % len(cols)

        with cols[col_index]:
            # Create a button for each suggestion
            if st.button(f"🔍 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                selected_suggestion = suggestion

    return selected_suggestion

def get_auto_parameters(product_name, purpose, cost, shelf_life, db):
    """Automatically determine the 15 parameters based on user inputs and database"""

    # Default parameters
    auto_params = {
        "product_state": "Liquid",
        "viscosity": "Medium",
        "ph_level": "Neutral",
        "oxygen_sensitivity": "Medium",
        "moisture_sensitivity": "Medium",
        "light_sensitivity": "Medium",
        "storage_temperature": "Ambient",
        "target_market": "Consumer retail",
        "industry_category": "Food",
        "budget_range": cost,
        "sustainability_priority": "Balanced",
        "safety_requirements": [],
        "brand_positioning": "Mainstream",
        "fragility_level": "Moderate",
        "shelf_life_requirement": shelf_life
    }

    # Check if product exists in database
    products = db.get("products", {})
    if product_name in products:
        stored_params = products[product_name].get("auto_parameters", {})
        auto_params.update(stored_params)
        auto_params["budget_range"] = cost  # Always use user input for cost
        auto_params["shelf_life_requirement"] = shelf_life  # Always use user input for shelf life
        return auto_params

    # Intelligent parameter detection based on product name and purpose
    product_lower = product_name.lower()
    purpose_lower = purpose.lower()

    # Beverages
    if any(word in product_lower for word in ["juice", "drink", "beverage", "soda", "water", "tea", "coffee"]):
        auto_params["industry_category"] = "Food"
        auto_params["product_state"] = "Liquid"
        auto_params["viscosity"] = "Low"
        auto_params["target_market"] = "Consumer retail"
        if any(word in product_lower for word in ["orange", "apple", "fruit"]):
            auto_params["oxygen_sensitivity"] = "High"
            auto_params["light_sensitivity"] = "High"
            auto_params["ph_level"] = "Acidic"

    # Dairy products
    elif any(word in product_lower for word in ["milk", "cheese", "butter", "yogurt", "cream"]):
        auto_params["industry_category"] = "Food"
        auto_params["product_state"] = "Liquid" if "milk" in product_lower else "Semi-solid"
        auto_params["storage_temperature"] = "Cold"
        auto_params["oxygen_sensitivity"] = "Medium"
        auto_params["light_sensitivity"] = "High"
        auto_params["shelf_life_requirement"] = "Weeks"

    # Oils and liquids
    elif any(word in product_lower for word in ["oil", "vinegar", "sauce", "honey", "syrup"]):
        auto_params["product_state"] = "Liquid"
        auto_params["viscosity"] = "High" if any(word in product_lower for word in ["honey", "syrup"]) else "Medium"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["light_sensitivity"] = "High"

    # Grains and dry goods
    elif any(word in product_lower for word in ["rice", "pasta", "flour", "cereal", "grain", "oats"]):
        auto_params["product_state"] = "Solid"
        auto_params["viscosity"] = "N/A"
        auto_params["moisture_sensitivity"] = "High"
        auto_params["oxygen_sensitivity"] = "Low"
        auto_params["storage_temperature"] = "Ambient"
        auto_params["brand_positioning"] = "Value"

    # Snacks
    elif any(word in product_lower for word in ["chips", "crackers", "cookies", "biscuits", "nuts"]):
        auto_params["product_state"] = "Solid"
        auto_params["viscosity"] = "N/A"
        auto_params["fragility_level"] = "Very Fragile" if "chips" in product_lower else "Fragile"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["moisture_sensitivity"] = "High"

    # Meat and fish
    elif any(word in product_lower for word in ["meat", "chicken", "fish", "beef", "pork"]):
        auto_params["product_state"] = "Solid"
        auto_params["storage_temperature"] = "Cold"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["shelf_life_requirement"] = "Days"
        auto_params["safety_requirements"] = ["Sterile"]

    # Frozen foods
    elif any(word in product_lower for word in ["frozen", "ice cream"]):
        auto_params["storage_temperature"] = "Frozen"
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["moisture_sensitivity"] = "High"

    # Canned goods
    elif any(word in product_lower for word in ["canned", "soup", "beans"]):
        auto_params["product_state"] = "Liquid" if "soup" in product_lower else "Semi-solid"
        auto_params["oxygen_sensitivity"] = "None"
        auto_params["moisture_sensitivity"] = "None"
        auto_params["shelf_life_requirement"] = "Years"
        auto_params["brand_positioning"] = "Value"

    # Confectionery
    elif any(word in product_lower for word in ["chocolate", "candy", "cake", "jam"]):
        auto_params["product_state"] = "Solid"
        auto_params["viscosity"] = "N/A"
        auto_params["moisture_sensitivity"] = "High"
        auto_params["light_sensitivity"] = "High"
        auto_params["brand_positioning"] = "Premium"

    # Baby food
    elif any(word in product_lower for word in ["baby", "infant"]):
        auto_params["product_state"] = "Semi-solid"
        auto_params["safety_requirements"] = ["Tamper evident"]
        auto_params["brand_positioning"] = "Premium"
        auto_params["oxygen_sensitivity"] = "High"

    # Purpose-based adjustments
    if "food" in purpose_lower or "storage" in purpose_lower:
        auto_params["oxygen_sensitivity"] = "High" if auto_params["oxygen_sensitivity"] == "Medium" else auto_params["oxygen_sensitivity"]

    elif "medical" in purpose_lower or "safety" in purpose_lower:
        auto_params["safety_requirements"] = ["Sterile", "Tamper evident"]
        auto_params["brand_positioning"] = "Premium"

    elif "display" in purpose_lower:
        auto_params["brand_positioning"] = "Premium"
        auto_params["sustainability_priority"] = "Balanced"

    # Cost-based adjustments
    if cost == "Premium":
        auto_params["brand_positioning"] = "Premium"
        auto_params["sustainability_priority"] = "Balanced"
    elif cost == "Economy":
        auto_params["brand_positioning"] = "Value"
        auto_params["sustainability_priority"] = "Cost focused"

    # Shelf life adjustments
    if shelf_life in ["Months", "Years"]:
        auto_params["oxygen_sensitivity"] = "High"
        auto_params["moisture_sensitivity"] = "High"
    elif shelf_life == "Days":
        auto_params["storage_temperature"] = "Cold"

    return auto_params

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

def get_packaging_recommendations(auto_params, db):
    """Generate intelligent packaging recommendations"""
    recommendations = []
    materials = db.get("packaging_materials", {})

    for material_name, material_data in materials.items():
        score, details = calculate_packaging_score(auto_params, material_name, material_data, db)

        recommendations.append({
            'name': material_name.replace('_', ' '),
            'material_name': material_name,
            'score': score,
            'data': material_data,
            'scoring_details': details,
            'reasons': generate_recommendation_reasons(auto_params, material_data, score)
        })

    # Sort by score (highest first)
    recommendations.sort(key=lambda x: x['score'], reverse=True)
    return recommendations

def generate_recommendation_reasons(auto_params, material_data, score):
    """Generate human-readable explanations for recommendations"""
    reasons = []

    # Product state compatibility
    if auto_params.get('product_state') in material_data['characteristics']['product_state_compatibility']:
        reasons.append(f"✅ Perfect for {auto_params.get('product_state').lower()} products")

    # Barrier properties
    barrier_reasons = []
    for barrier_type in ['oxygen', 'moisture', 'light']:
        user_need = auto_params.get(f'{barrier_type}_sensitivity', 'None')
        material_barrier = material_data['characteristics'][f'{barrier_type}_barrier']

        if user_need == 'High' and material_barrier in ['Excellent', 'High']:
            barrier_reasons.append(f"{barrier_type}")

    if barrier_reasons:
        reasons.append(f"🛡️ Excellent {', '.join(barrier_reasons)} protection")

    # Cost alignment
    if auto_params.get('budget_range') == material_data['characteristics']['cost_category']:
        reasons.append(f"💰 Matches {auto_params.get('budget_range').lower()} budget perfectly")

    # Sustainability
    if auto_params.get('sustainability_priority') == 'Eco-focused':
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
    st.markdown("*AI-Powered Packaging Recommendations - Just 4 Simple Questions!*")
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
    st.markdown("*Answer just 4 simple questions to get AI-powered packaging suggestions*")

    # Create a centered form
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            st.markdown("### 📝 Tell us about your product")

            # Question 1: Product Name with Search Suggestions
            st.markdown("🏷️ **1. What is your product name?**")

            # Initialize session state for product name if not exists
            if 'product_name_input' not in st.session_state:
                st.session_state.product_name_input = ""

            # Create text input
            product_name_query = st.text_input(
                "Product Name:",
                value=st.session_state.product_name_input,
                placeholder="e.g., Orange Juice, Potato Chips, Chocolate...",
                help="Start typing and see suggestions appear",
                label_visibility="collapsed"
            )

            # Get and display suggestions
            if product_name_query and len(product_name_query) >= 1:
                suggestions = get_search_suggestions(product_name_query, db)
                if suggestions:
                    selected_suggestion = display_search_suggestions(suggestions, product_name_query)
                    if selected_suggestion:
                        st.session_state.product_name_input = selected_suggestion
                        product_name_query = selected_suggestion
                        st.rerun()

            # Use the final product name
            product_name = product_name_query

            # Show if product is in database
            if product_name and product_name in db.get("products", {}):
                st.success(f"✅ Found '{product_name}' in our database!")
            elif product_name and len(product_name) > 2:
                st.info(f"📦 Will analyze '{product_name}' using AI detection")

            st.markdown("---")

            # Question 2: Purpose
            purpose = st.selectbox(
                "🎯 **2. What is the main purpose of packaging?**",
                ["Protection & Storage", "Retail Display", "Transportation", "Medical Safety", "Food Safety", "Industrial Use"],
                help="Select the primary purpose for your packaging"
            )

            # Question 3: Cost
            cost = st.selectbox(
                "💰 **3. What is your budget preference?**",
                ["Economy", "Standard", "Premium"],
                help="Choose your packaging budget level"
            )

            # Question 4: Shelf Life
            shelf_life = st.selectbox(
                "⏰ **4. How long should the product last?**",
                ["Days", "Weeks", "Months", "Years"],
                help="Select the expected shelf life of your product"
            )

    st.markdown("---")

    # Generate recommendations button
    if st.button("🎯 Get My Packaging Recommendations", type="primary", use_container_width=True):
        if not product_name:
            st.error("❌ Please enter a product name first!")
            return

        with st.spinner("🤖 AI is analyzing your product and generating recommendations..."):
            # Get auto-generated parameters
            auto_params = get_auto_parameters(product_name, purpose, cost, shelf_life, db)

            # Get recommendations
            recommendations = get_packaging_recommendations(auto_params, db)

        # CHECK IF RECOMMENDATIONS EXIST - FIX FOR THE ERROR
        if not recommendations:
            st.error("❌ No packaging materials found in database. Please check your database configuration.")
            return

        st.success(f"🎉 Here are the packaging recommendations for **{product_name}**!")

        # Show what AI detected
        with st.expander("🔍 What our AI detected about your product", expanded=False):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write("**Product Analysis:**")
                st.write(f"• Industry: {auto_params['industry_category']}")
                st.write(f"• State: {auto_params['product_state']}")
                st.write(f"• Target Market: {auto_params['target_market']}")

            with col2:
                st.write("**Protection Needs:**")
                st.write(f"• Oxygen: {auto_params['oxygen_sensitivity']}")
                st.write(f"• Moisture: {auto_params['moisture_sensitivity']}")
                st.write(f"• Light: {auto_params['light_sensitivity']}")

            with col3:
                st.write("**Requirements:**")
                st.write(f"• Storage: {auto_params['storage_temperature']}")
                st.write(f"• Positioning: {auto_params['brand_positioning']}")
                st.write(f"• Sustainability: {auto_params['sustainability_priority']}")

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
                    for detail in rec['scoring_details'][:4]:  # Show top 4 scoring details
                        st.write(f"• {detail}")

                with col_reasons:
                    st.write("**Why This Packaging:**")
                    for reason in rec['reasons']:
                        st.write(f"• {reason}")

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

        # FINAL RECOMMENDATIONS SUMMARY - FIXED WITH ERROR CHECKING
        st.markdown("---")
        st.markdown(f"## 📦 **Final Packaging Recommendations for {product_name}**")

        if recommendations and len(recommendations) > 0:
            top_3 = recommendations[:3]

            col1, col2, col3 = st.columns(3)

            for i, rec in enumerate(top_3):
                with [col1, col2, col3][i]:
                    # Determine emoji based on score
                    if rec['score'] >= 75:
                        emoji = "🏆"
                        color = "28a745"
                    elif rec['score'] >= 50:
                        emoji = "🥈"
                        color = "ffc107"
                    else:
                        emoji = "🥉"
                        color = "17a2b8"

                    st.markdown(f"""
                    <div style="border: 2px solid #{color}; 
                                border-radius: 10px; padding: 15px; text-align: center; margin: 5px;">
                        <h4>{emoji} #{i+1} CHOICE</h4>
                        <h3>{rec['name']}</h3>
                        <h2 style="color: #{color}">
                            {rec['score']:.0f}% Match
                        </h2>
                        <p><strong>Type:</strong> {rec['data']['material_type']}</p>
                        <p><strong>Cost:</strong> {rec['data']['characteristics']['cost_category']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Key benefits
                    st.markdown("**🔑 Key Benefits:**")
                    for reason in rec['reasons'][:3]:
                        st.markdown(f"• {reason}")

                    if i == 0:  # Best choice
                        st.markdown("**🎯 RECOMMENDED CHOICE**")

            # Summary message - FIXED WITH SAFE ACCESS
            st.markdown("---")
            if len(recommendations) > 0:
                best_recommendation = recommendations[0]
                st.info(f"""
                **💡 Summary:** Based on your product '{product_name}' with {purpose.lower()} purpose, 
                {cost.lower()} budget, and {shelf_life.lower()} shelf life, we recommend **{best_recommendation['name']}** 
                as your best packaging solution with a {best_recommendation['score']:.0f}% compatibility match.
                """)
        else:
            st.warning("⚠️ No recommendations could be generated. Please check your database configuration.")

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
    st.markdown("*Add a new product to the database*")

    product_name = st.text_input("Product Name:", placeholder="e.g., Premium Face Serum")

    if product_name:
        if product_name in db.get("products", {}):
            st.error(f"Product '{product_name}' already exists!")
            return

        # Simplified input using the 4-question format
        purpose = st.selectbox("Purpose:", ["Protection & Storage", "Retail Display", "Transportation", "Medical Safety", "Food Safety", "Industrial Use"])
        cost = st.selectbox("Budget:", ["Economy", "Standard", "Premium"])
        shelf_life = st.selectbox("Shelf Life:", ["Days", "Weeks", "Months", "Years"])

        if st.button("💾 Save Product", type="primary"):
            # Generate auto parameters
            auto_params = get_auto_parameters(product_name, purpose, cost, shelf_life, db)

            new_product = {
                "basic_info": {
                    "category": auto_params["industry_category"],
                    "subcategory": "Auto-detected",
                    "intended_market": auto_params["target_market"]
                },
                "properties": {
                    "weight_volume": "Auto-detected",
                    "shape_form": auto_params["product_state"],
                    "shelf_life": shelf_life,
                    "fragility": auto_params["fragility_level"],
                    "moisture_sensitivity": "Yes" if auto_params["moisture_sensitivity"] in ["Medium", "High"] else "No",
                    "light_sensitivity": "Yes" if auto_params["light_sensitivity"] in ["Medium", "High"] else "No"
                },
                "packaging": {
                    "primary": [],
                    "secondary": [],
                    "tertiary": []
                },
                "auto_parameters": auto_params,
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
        st.write("✅ Google-like Search Suggestions")
        st.write("✅ Just 4 Simple Questions")
        st.write("✅ Auto Parameter Detection")
        st.write("✅ Advanced Scoring Algorithm")
        st.write("✅ Technical Material Database")
        st.write("✅ Sustainability Analysis")
        st.write("✅ Cost Optimization")

    st.subheader("🤖 How It Works")
    st.write("""
    **Smart Packaging Advisor Pro** uses AI to:
    1. **Search** with Google-like suggestions as you type
    2. **Analyze** your product name and purpose
    3. **Auto-detect** 15+ technical parameters  
    4. **Score** compatibility with packaging materials
    5. **Recommend** the best 3 packaging solutions
    6. **Explain** why each solution works for your product
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
