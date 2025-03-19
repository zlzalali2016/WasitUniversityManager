import streamlit as st
import json
import os

def init_auth():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    # Create users.json if it doesn't exist
    if not os.path.exists('data/users.json'):
        os.makedirs('data', exist_ok=True)
        with open('data/users.json', 'w', encoding='utf-8') as f:
            json.dump({
                "admin": "admin123"  # Default admin credentials
            }, f)

def check_login(username, password):
    try:
        with open('data/users.json', 'r', encoding='utf-8') as f:
            users = json.load(f)
            return username in users and users[username] == password
    except Exception as e:
        st.error(f"خطأ في التحقق من بيانات المستخدم: {str(e)}")
        return False
