import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

def login():

    st.sidebar.title("User Login")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):

        users = db.collection("users").where("email","==",email).get()

        for u in users:
            if u.to_dict()["password"] == password:
                st.session_state["user"] = email
                return True

        st.sidebar.error("Invalid Login")

    return False


def save_account(user,account):

    db.collection("accounts").add({
        "user":user,
        "account":account
    })


def get_accounts(user):

    docs=db.collection("accounts").where("user","==",user).get()

    return [d.to_dict()["account"] for d in docs]
