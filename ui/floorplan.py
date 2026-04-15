import streamlit as st
from PIL import Image

def upload_floorplan():

    file = st.file_uploader("Grundriss hochladen", type=["png","jpg"])

    if file:
        img = Image.open(file)
        st.image(img)
        return img

    return None


def define_rooms():

    if "rooms_pos" not in st.session_state:
        st.session_state["rooms_pos"] = []

    name = st.text_input("Raumname")
    x = st.number_input("X", 0, 2000, 100)
    y = st.number_input("Y", 0, 2000, 100)

    if st.button("Raum hinzufügen"):
        st.session_state["rooms_pos"].append({
            "name": name,
            "x": x,
            "y": y
        })

    return st.session_state["rooms_pos"]
