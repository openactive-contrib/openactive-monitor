import streamlit as st

# Sample list of logo URLs (replace with your actual list)
logo_urls = [
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",
    "https://www.openactive.io/wp-content/themes/open-active-1_3/images/favicon.png",
    "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/768px-Instagram_logo_2016.svg.png",

]
import streamlit as st
import time

st.header("test")

if 'show_logos' not in st.session_state:
    st.session_state.show_logos = False

def toggle_logos():
    st.session_state.show_logos = not st.session_state.show_logos

st.button("Show/Hide Logos", on_click=toggle_logos)

if st.session_state.show_logos:
    # Container for the scrolling effect
    logo_container = st.container()  

    for i, url in enumerate(logo_urls):
        with logo_container:
            st.image(url, width=100)
            time.sleep(0.3)  # Delay for 300ms

