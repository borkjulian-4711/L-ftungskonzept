import streamlit as st
from PIL import Image

def upload_floorplan():

    uploaded_file = st.file_uploader("Grundriss hochladen", type=["png","jpg","jpeg"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)
        return image

    return None


def define_rooms():

    st.subheader("Räume im Grundriss definieren")

    if "rooms_pos" not in st.session_state:
        st.session_state["rooms_pos"] = []

    room_name = st.text_input("Raumname")

    x = st.number_input("X-Position", 0, 2000, 100)
    y = st.number_input("Y-Position", 0, 2000, 100)

    if st.button("Raum hinzufügen"):

        st.session_state["rooms_pos"].append({
            "name": room_name,
            "x": x,
            "y": y
        })

    return st.session_state["rooms_pos"]
