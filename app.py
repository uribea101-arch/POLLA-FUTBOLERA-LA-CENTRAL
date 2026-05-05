import streamlit as st

st.title("⚽ Polla Futbolera")

equipo1 = "Equipo A"
equipo2 = "Equipo B"
hora = "00:00"

st.subheader(f"{equipo1} vs {equipo2}")
st.write(f"🕒 {hora}")

st.caption("Recuerda que solo es un marcador por cédula.")

usuario = st.text_input("Correo o cédula")
goles1 = st.number_input(equipo1, min_value=0, max_value=20)
goles2 = st.number_input(equipo2, min_value=0, max_value=20)

if st.button("Enviar"):
    if usuario:
        st.success("Marcador registrado ✅")
    else:
        st.error("Debes ingresar un dato válido")
