#import switch_page # pyright: ignore[reportMissingImports]
from collections import defaultdict
import streamlit as st
import mysql.connector
import hashlib
from datetime import datetime
import os
import pandas as pd

# --- DB Connection ---
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1127",
        database="Test1"
    )

# --- Password Hashing ---
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(password, stored):
    #salt, hashed = stored.split('$')
    #return hashlib.sha256((salt + password).encode()).hexdigest() == hashed
    return hashlib.sha256((password).encode()).hexdigest()


# --- Login User  ---
def login_user(username, password ):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM login WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()
    if user and check_password(password, user['password']):
        return user["role"]
    return None
# --- Inserting query ---
def insert_query(email, mobile, heading, description):
    conn = get_db_connection()
    cursor = conn.cursor()
    created_time = datetime.now()
    status = "Open"
    cursor.execute("""
        INSERT INTO client_queries 
        (email_id, mobile_number, query_heading, query_description, query_created_time, status, query_closed_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (email, mobile, heading, description, created_time, status, None))
    conn.commit()
    cursor.close()
    conn.close()
# --- Fetching Categories ---
def fetch_categories():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT query_heading FROM client_queries")
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    conn.close()
    return categories
# --- Fetching Queries ---
def fetch_queries(status_filter=None, heading_filter=None):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM client_queries WHERE 1=1"
    params = []

    if status_filter and status_filter != "All":
        query += " AND status = %s"
        params.append(status_filter)

    if heading_filter and heading_filter != "All":
        query += " AND query_heading = %s"
        params.append(heading_filter)

    cursor.execute(query, params)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# --- Closing Queries ---
def close_query(query_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    closed_time = datetime.now()
    cursor.execute("""
        UPDATE client_queries 
        SET status = %s, query_closed_time = %s 
        WHERE id = %s
    """, ("Closed", closed_time, query_id))
    conn.commit()
    cursor.close()
    conn.close()

# --- Login Page ---
def home():
    st.title("🔐 Login Page")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    role = st.selectbox("Role",("Client","Support"),index=None, placeholder="Select your appropriate Role Here ")

    if st.button("Login"):
        role = login_user(username, password)
        if role:
            st.session_state.authenticated = True
            st.session_state.role = role
            st.session_state.username = username
            st.session_state.page = role   # "client" or "support"
            st.success(f"✅ Login successful! You are logged in as **{role}**.")
            #st.experimental_rerun()
        else:                                    
            st.error("❌ Invalid credentials")
# --- Client Page ---
def client_page():
     st.title("📩 Client Query Submission")

     with st.form("query_form"):
        email = st.text_input("Email ID")
        mobile = st.text_input("Mobile Number")
        heading = st.text_input("Query Heading")
        description = st.text_area("Query Description")
        
        submitted = st.form_submit_button("Submit Query")
        ##insert_query=INSERT INTO client_queries (email,mobile,heading,description) values(%s,%s,%s,%s)
        if submitted:
            if email and mobile and heading and description:
                insert_query(email, mobile, heading, description)
                st.success("✅ Query submitted successfully!")
            else:
                st.error("⚠️ Please fill all fields.")

     if st.button("⬅️ Logout"):
            st.session_state.authenticated = False
            st.session_state.page = "home"

# --- Support Page ---    
def support_page():
     st.title("🛠️ Query Management (Support Team)")

    # Filters
     status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed"], placeholder="Choose Status")
     categories = fetch_categories()
     heading_filter = st.selectbox("Filter by Category", categories, placeholder="Select Your Category")
     
    # Fetch and display queries
     queries = fetch_queries(status_filter, heading_filter)
     
     if queries:
        df = pd.DataFrame(queries)
        st.dataframe(df)

          
        ##Close query option (only for Open queries)
        open_queries = [q for q in queries if q["status"] == "Open"]
        if open_queries:
            query_to_close = st.selectbox(
                "Select a query to close",
                options=[f'{q["id"]}: {q["query_heading"]}' for q in open_queries]
       
            )
            if st.button("Close Selected Query"):
                selected_id = int(query_to_close.split(":")[0])
                close_query(selected_id)
                st.success(f"✅ Query ID {selected_id} closed successfully!")
                ##st.rerun()
            else:
                st.info("✅ No open queries available.")
        else:
            st.info("No queries found for the selected filters.")



        if st.button("⬅️ Logout"):
            st.session_state.authenticated = False
            st.session_state.page = "home"
      


# ---- Streamlit App  ----
st.set_page_config(page_title="Login Navigation", layout="centered")

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False   
    st.session_state.role = None
    st.session_state.username = None
    st.session_state.page = "home"

# ---- Debug Info (you can remove later) ----

##st.sidebar.write("🔎 Debug State:")
##st.sidebar.json({
    ##"authenticated": st.session_state.authenticated,
    ##"role": st.session_state.role,
    ##"page": st.session_state.page
##})

# ---- Routing ----
if st.session_state.page == "home":
    home()
elif st.session_state.page == "Client":
    if st.session_state.authenticated and st.session_state.role == "Client":

        client_page()
    else:
        st.error("⚠️ Access denied. Please login as Client.")
        home()
elif st.session_state.page == "Support":
    if st.session_state.authenticated and st.session_state.role == "Support":
        support_page()
    else:
        st.error("⚠️ Access denied. Please login as Support.")
        home()

