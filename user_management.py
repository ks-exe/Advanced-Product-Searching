import streamlit as st
import hashlib
import json
from pathlib import Path
import os

# User data storage
USERS_FILE = "users.json"

def init_users_file():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, email):
    init_users_file()
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if username in users:
        return False, "Username already exists"
    
    users[username] = {
        "password": hash_password(password),
        "email": email,
        "cart": [],
        "wishlist": []
    }
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f)
    
    return True, "Registration successful"

def login_user(username, password):
    init_users_file()
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if username not in users:
        return False, "User not found"
    
    if users[username]["password"] != hash_password(password):
        return False, "Incorrect password"
    
    return True, "Login successful"

def get_user_data(username):
    init_users_file()
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    return users.get(username)

def update_user_data(username, data):
    init_users_file()
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if username in users:
        users[username].update(data)
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f)
        return True
    return False

def add_to_cart(username, product_id):
    user_data = get_user_data(username)
    if user_data:
        if product_id not in user_data["cart"]:
            user_data["cart"].append(product_id)
            update_user_data(username, user_data)
            return True
    return False

def remove_from_cart(username, product_id):
    user_data = get_user_data(username)
    if user_data and product_id in user_data["cart"]:
        user_data["cart"].remove(product_id)
        update_user_data(username, user_data)
        return True
    return False

def get_cart(username):
    user_data = get_user_data(username)
    return user_data["cart"] if user_data else [] 