import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from product_data import (
    products, products_by_category, products_by_brand,
    search_by_price_range, search_by_top_ratings,
    add_product_obj, remove_product_obj
)
from models import Product
from search_algorithms import SearchAlgorithms
import difflib
from user_management import (
    register_user, login_user, add_to_cart, remove_from_cart, 
    get_cart, get_user_data, update_user_data
)
import json
import time

# Set page configuration - must be the first Streamlit command
st.set_page_config(
    page_title="KS - Advanced Product Search",
    page_icon="🛍️",
    layout="wide"
)

# Initialize search algorithms
search_algo = SearchAlgorithms(products)

# Custom CSS for better UI
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    .product-card {
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #e0e0e0;
        margin-bottom: 1rem;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .product-card:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
        transition: all 0.3s ease;
    }
    .search-results {
        margin-top: 2rem;
    }
    .algorithm-comparison {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .suggestion-item {
        padding: 0.5rem;
        cursor: pointer;
        border-radius: 5px;
    }
    .suggestion-item:hover {
        background-color: #f0f0f0;
    }
    .search-box {
        position: relative;
    }
    .search-suggestions {
        position: absolute;
        top: 100%;
        left: 0;
        right: 0;
        background: white;
        border: 1px solid #ddd;
        border-radius: 0 0 5px 5px;
        z-index: 1000;
        max-height: 200px;
        overflow-y: auto;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for persistent login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'username' not in st.session_state:
    st.session_state.username = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
if 'compare_products' not in st.session_state:
    st.session_state.compare_products = []
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'show_suggestions' not in st.session_state:
    st.session_state.show_suggestions = False
if 'selected_suggestion' not in st.session_state:
    st.session_state.selected_suggestion = None

# Function Definitions
def show_search_box():
    st.markdown("### 🔍 Advanced Product Search")
    
    # Create a container for the search box
    search_container = st.container()
    
    with search_container:
        # Search input
        query = st.text_input(
            "Search products...",
            value=st.session_state.search_query,
            key="search_input",
            placeholder="Type to search (e.g., 'iPhone', 'Samsung', 'Laptop')"
        )
        
        # Update session state
        if query != st.session_state.search_query:
            st.session_state.search_query = query
            st.session_state.show_suggestions = True
        
        # Show suggestions
        if st.session_state.show_suggestions and query:
            suggestions = search_algo.get_suggestions(query)
            if suggestions:
                st.markdown("### Suggestions")
                for suggestion in suggestions:
                    if st.button(suggestion, key=f"suggestion_{suggestion}"):
                        st.session_state.search_query = suggestion
                        st.session_state.show_suggestions = False
                        st.rerun()

def show_search_results(query):
    if not query:
        return
    
    st.markdown("### Search Results")
    
    # Run all search algorithms
    results = search_algo.run_all_searches(query)
    
    # Create comparison chart
    algo_names = [r.algorithm_name for r in results.values()]
    times = [r.time_taken * 1000 for r in results.values()]  # Convert to milliseconds
    matches = [r.matches_found for r in results.values()]
    
    # Performance comparison chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Time (ms)',
        x=algo_names,
        y=times,
        text=[f'{t:.2f}ms' for t in times],
        textposition='auto',
    ))
    fig.add_trace(go.Bar(
        name='Matches Found',
        x=algo_names,
        y=matches,
        text=matches,
        textposition='auto',
    ))
    
    fig.update_layout(
        title='Search Algorithm Performance Comparison',
        barmode='group',
        xaxis_title='Algorithm',
        yaxis_title='Value',
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display results from each algorithm
    for algo_name, result in results.items():
        with st.expander(f"{result.algorithm_name} Results ({result.matches_found} matches, {result.time_taken*1000:.2f}ms)"):
            if result.products:
                for idx, product in enumerate(result.products):
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="product-card">
                                <h3>{product.name}</h3>
                                <p><strong>Brand:</strong> {product.brand}</p>
                                <p><strong>Price:</strong> PKR {product.price:,}</p>
                                <p><strong>Rating:</strong> {'⭐' * product.rating}</p>
                                <p><strong>Availability:</strong> {product.availability}</p>
                                <p>{product.description}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("Add to Cart", key=f"{algo_name}_cart_{product.pid}_{idx}"):
                                add_to_cart(st.session_state.username, product.pid)
                                st.success("Added to cart!")
                            if st.button("Compare", key=f"{algo_name}_compare_{product.pid}_{idx}"):
                                add_to_compare(product.pid)
                                st.success("Added to comparison!")
            else:
                st.write("No products found")

def show_login_form():
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        if not username or not password:
            st.error("Please enter both username and password")
            return
        success, message = login_user(username, password)
        if success:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_data = get_user_data(username)
            st.success(message)
            st.rerun()
        else:
            st.error(message)

def show_register_form():
    st.subheader("Register")
    username = st.text_input("Username", key="register_username")
    password = st.text_input("Password", type="password", key="register_password")
    email = st.text_input("Email", key="register_email")
    if st.button("Register", key="register_button"):
        if not username or not password or not email:
            st.error("Please fill in all fields")
            return
        success, message = register_user(username, password, email)
        if success:
            st.success(message)
        else:
            st.error(message)

def show_cart():
    st.subheader("Shopping Cart")
    cart_items = get_cart(st.session_state.username)
    if not cart_items:
        st.write("Your cart is empty")
        return
    
    total = 0
    for product_id in cart_items:
        product = next((p for p in products if p.pid == product_id), None)
        if product:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{product.name}** - PKR {product.price:,}")
            with col2:
                st.write(f"Rating: {'⭐' * product.rating}")
            with col3:
                if st.button("Remove", key=f"cart_remove_{product_id}"):
                    remove_from_cart(st.session_state.username, product_id)
                    st.rerun()
            total += product.price
    
    st.write(f"**Total: PKR {total:,}**")
    if st.button("Checkout", key="cart_checkout"):
        st.success("Order placed successfully!")
        # Clear cart after checkout
        user_data = get_user_data(st.session_state.username)
        if user_data:
            user_data["cart"] = []
            update_user_data(st.session_state.username, user_data)
            st.rerun()

def add_to_compare(product_id):
    if product_id not in st.session_state.compare_products:
        st.session_state.compare_products.append(product_id)
        if len(st.session_state.compare_products) > 3:
            st.session_state.compare_products.pop(0)

def show_compare_products():
    if not st.session_state.compare_products:
        st.write("No products selected for comparison")
        return
    
    compare_data = []
    for pid in st.session_state.compare_products:
        product = next((p for p in products if p.pid == pid), None)
        if product:
            compare_data.append({
                'Name': product.name,
                'Brand': product.brand,
                'Price': f"PKR {product.price:,}",
                'Rating': '⭐' * product.rating,
                'Availability': product.availability,
                'Category': product.category
            })
    
    if compare_data:
        df = pd.DataFrame(compare_data)
        st.table(df)
        
        if st.button("Clear Comparison", key="clear_comparison"):
            st.session_state.compare_products = []
            st.rerun()

# Convert products to DataFrame for easier manipulation
def get_products_df():
    data = []
    for product in products:
        data.append({
            'ID': product.pid,
            'Name': product.name,
            'Brand': product.brand,
            'Price': product.price,
            'Availability': product.availability,
            'Category': product.category,
            'Rating': product.rating,
            'Description': product.description
        })
    return pd.DataFrame(data)

# Function to check login status
def check_login_status():
    if st.session_state.logged_in and st.session_state.username:
        # Only fetch user data if we don't have it
        if not st.session_state.user_data:
            user_data = get_user_data(st.session_state.username)
            if user_data:
                st.session_state.user_data = user_data
                return True
            else:
                # If user data can't be fetched, clear the session
                handle_logout()
                return False
        return True
    return False

# Function to handle login
def handle_login(username, password):
    success, message = login_user(username, password)
    if success:
        user_data = get_user_data(username)
        if user_data:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.session_state.user_data = user_data
            st.success(message)
            st.rerun()
        else:
            st.error("Failed to fetch user data. Please try again.")
    else:
        st.error(message)

# Function to handle logout
def handle_logout():
    st.session_state.logged_in = False
    st.session_state.username = None
    st.session_state.user_data = None
    st.rerun()

# Main content
st.title("🛍️ KS - Advanced Product Search")
st.markdown("Welcome to KS, your one-stop shop for finding the perfect products!")

# Check login status
is_logged_in = check_login_status()

# Authentication Section
if not is_logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        show_login_form()
    with tab2:
        show_register_form()
else:
    st.sidebar.write(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout", key="logout_button"):
        handle_logout()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "Advanced Search", "Top Rated", "Analytics", 
        "Shopping Cart", "Compare Products", "Manage Products"
    ])
    
    with tab1:
        show_search_box()
        if st.session_state.search_query:
            show_search_results(st.session_state.search_query)
    
    with tab2:
        st.header("Top Rated Products")
        top_products = search_by_top_ratings(10)
        for product in top_products:
            with st.container():
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="product-card">
                        <h3>{product.name}</h3>
                        <p><strong>Brand:</strong> {product.brand}</p>
                        <p><strong>Price:</strong> PKR {product.price:,}</p>
                        <p><strong>Rating:</strong> {'⭐' * product.rating}</p>
                        <p><strong>Availability:</strong> {product.availability}</p>
                        <p>{product.description}</p>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("Add to Cart", key=f"top_cart_{product.pid}"):
                        add_to_cart(st.session_state.username, product.pid)
                        st.success("Added to cart!")
                    if st.button("Compare", key=f"top_compare_{product.pid}"):
                        add_to_compare(product.pid)
                        st.success("Added to comparison!")
    
    with tab3:
        st.header("Product Analytics")
        df = get_products_df()
        
        # Price distribution by category
        st.subheader("Price Distribution by Category")
        fig = px.box(df, x="Category", y="Price", title="Price Distribution by Category")
        st.plotly_chart(fig, use_container_width=True)
        
        # Rating distribution
        st.subheader("Rating Distribution")
        fig = px.histogram(df, x="Rating", title="Product Ratings Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        # Availability status
        st.subheader("Product Availability")
        availability_counts = df["Availability"].value_counts()
        fig = px.pie(values=availability_counts.values, names=availability_counts.index, title="Product Availability")
        st.plotly_chart(fig, use_container_width=True)
        
        # Brand distribution
        st.subheader("Products by Brand")
        brand_counts = df["Brand"].value_counts()
        fig = px.bar(x=brand_counts.index, y=brand_counts.values, title="Number of Products by Brand")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        show_cart()
    
    with tab5:
        st.header("Compare Products")
        show_compare_products()
    
    with tab6:
        st.header("Manage Products")
        
        # Add new product
        st.subheader("Add New Product")
        with st.form("add_product_form"):
            new_name = st.text_input("Product Name", key="new_product_name")
            new_brand = st.text_input("Brand", key="new_product_brand")
            new_price = st.number_input("Price (PKR)", min_value=0, key="new_product_price")
            new_availability = st.selectbox("Availability", ["In Stock", "Out of Stock"], key="new_product_availability")
            new_description = st.text_area("Description", key="new_product_description")
            new_category = st.selectbox("Category", list(products_by_category.keys()) + ["New Category"], key="new_product_category")
            if new_category == "New Category":
                new_category = st.text_input("Enter New Category", key="new_category_input")
            new_rating = st.slider("Rating", 1, 5, 3, key="new_product_rating")
            
            submitted = st.form_submit_button("Add Product")
            if submitted:
                if not all([new_name, new_brand, new_price, new_availability, new_description, new_category]):
                    st.error("Please fill in all fields")
                else:
                    # Get the next available product ID
                    new_pid = max(p.pid for p in products) + 1 if products else 1
                    # Create new product
                    new_product = Product(new_pid, new_name, new_brand, new_price, 
                                        new_availability, new_description, new_category, new_rating)
                    add_product_obj(new_product)
                    st.success(f"Product '{new_name}' added successfully!")
                    st.rerun()
        
        # Edit/Delete existing products
        st.subheader("Manage Existing Products")
        product_df = get_products_df()
        st.dataframe(product_df)
        
        # Edit product
        st.subheader("Edit Product")
        edit_pid = st.selectbox("Select Product to Edit", 
                              options=[p.pid for p in products],
                              format_func=lambda x: f"{x} - {next(p.name for p in products if p.pid == x)}",
                              key="edit_product_select")
        
        if edit_pid:
            product_to_edit = next(p for p in products if p.pid == edit_pid)
            with st.form("edit_product_form"):
                edit_name = st.text_input("Product Name", value=product_to_edit.name, key="edit_product_name")
                edit_brand = st.text_input("Brand", value=product_to_edit.brand, key="edit_product_brand")
                edit_price = st.number_input("Price (PKR)", min_value=0, value=product_to_edit.price, key="edit_product_price")
                edit_availability = st.selectbox("Availability", ["In Stock", "Out of Stock"], 
                                              index=0 if product_to_edit.availability == "In Stock" else 1,
                                              key="edit_product_availability")
                edit_description = st.text_area("Description", value=product_to_edit.description, key="edit_product_description")
                edit_category = st.selectbox("Category", list(products_by_category.keys()) + ["New Category"],
                                          index=list(products_by_category.keys()).index(product_to_edit.category) 
                                          if product_to_edit.category in products_by_category.keys() else len(products_by_category.keys()),
                                          key="edit_product_category")
                if edit_category == "New Category":
                    edit_category = st.text_input("Enter New Category", value=product_to_edit.category, key="edit_category_input")
                edit_rating = st.slider("Rating", 1, 5, product_to_edit.rating, key="edit_product_rating")
                
                submitted = st.form_submit_button("Update Product")
                if submitted:
                    if not all([edit_name, edit_brand, edit_price, edit_availability, edit_description, edit_category]):
                        st.error("Please fill in all fields")
                    else:
                        # Remove old product
                        remove_product_obj(edit_pid)
                        # Add updated product
                        updated_product = Product(edit_pid, edit_name, edit_brand, edit_price,
                                                edit_availability, edit_description, edit_category, edit_rating)
                        add_product_obj(updated_product)
                        st.success(f"Product '{edit_name}' updated successfully!")
                        st.rerun()
        
        # Delete product
        st.subheader("Delete Product")
        delete_pid = st.selectbox("Select Product to Delete",
                                options=[p.pid for p in products],
                                format_func=lambda x: f"{x} - {next(p.name for p in products if p.pid == x)}",
                                key="delete_product_select")
        
        if delete_pid:
            if st.button("Delete Product", key="delete_product_button"):
                product_to_delete = next(p for p in products if p.pid == delete_pid)
                if remove_product_obj(delete_pid):
                    st.success(f"Product '{product_to_delete.name}' deleted successfully!")
                    st.rerun()
                else:
                    st.error("Failed to delete product")

# Footer
st.markdown("---")
st.markdown("© 2025 KS - Advanced Product Search System") 