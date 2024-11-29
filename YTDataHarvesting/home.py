import streamlit as st

html_file = "hometext.html"

# Display the HTML file
st.markdown(open(html_file).read(), unsafe_allow_html=True)