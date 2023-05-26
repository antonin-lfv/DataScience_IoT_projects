import streamlit as st
import base64


def interpret_air_quality(value):
    if value < 100:
        return "Fresh Air"
    elif value < 200:
        return "Low Pollution"
    else:
        return "High Pollution"


def sidebar_bg(side_bg):
    side_bg_ext = 'png'

    st.markdown(
        f"""
      <style>
      [data-testid="stSidebar"] > div:first-child {{
          background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
      }}
      </style>
      """,
        unsafe_allow_html=True,
    )
