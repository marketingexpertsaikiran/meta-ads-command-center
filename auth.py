import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st

cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

def login():

    st.sidebar.title("Login")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):

        user_ref = db.collection("users").document(email)
        user = user_ref.get()

        if user.exists:
            st.session_state["user"] = email
            st.success("Logged in")
        else:
            st.error("User not found")


def save_account(account_id, token):

    user = st.session_state["user"]

    db.collection("accounts").add({
        "user": user,
        "account_id": account_id,
        "token": token
    })


def get_accounts():

    user = st.session_state["user"]

    docs = db.collection("accounts").where("user", "==", user).stream()

    accounts = []

    for doc in docs:
        accounts.append(doc.to_dict())

    return accounts
