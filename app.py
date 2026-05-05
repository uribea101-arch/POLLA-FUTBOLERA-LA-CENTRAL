import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# 🔐 Conexión con Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)

client = gspread.authorize(creds)

sheet = client.open("Polla Futbolera").sheet1

# 📊 Leer datos actuales
data = sheet.get_all_records()
df = pd.DataFrame(data)

# ⚽ Configuración del partido
equipo1 = "Medellín"
equipo2 = "Nacional"
hora = "7:30 PM"

st.title("⚽ Polla Futbolera")
st.subheader(f"{equipo1} vs {equipo2}")
st.write(f"🕒 {hora}")
st.caption("Recuerda que solo es un marcador por cédula.")

# 🧾 Formulario
usuario = st.text_input("Correo o cédula")
goles1 = st.number_input(equipo1, min_value=0, max_value=20)
goles2 = st.number_input(equipo2, min_value=0, max_value=20)

if st.button("Enviar"):
    if not usuario:
        st.error("Debes ingresar un dato válido")
    else:
        # 🔒 Validar duplicado
        if not df.empty and usuario in df["usuario"].values:
            st.warning("Ya registraste un marcador ❌")
        else:
            # 💾 Guardar en Sheets
            sheet.append_row([
                usuario,
                goles1,
                goles2,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            st.success("Marcador registrado ✅")
