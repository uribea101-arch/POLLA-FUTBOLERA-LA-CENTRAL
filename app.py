import streamlit as st
import firebase_admin

from firebase_admin import credentials
from firebase_admin import firestore

st.title("🔥 Test Firebase")

try:

    # 🔐 iniciar firebase
    if not firebase_admin._apps:

        cred = credentials.Certificate(
            dict(st.secrets["gcp_service_account"])
        )

        firebase_admin.initialize_app(cred)

    # 🔥 conectar firestore
    db = firestore.client()

    # 🧪 escribir prueba
    db.collection("test").add({
        "ok": True
    })

    st.success("🔥 FIRESTORE FUNCIONA")

except Exception as e:

    st.error(e)
