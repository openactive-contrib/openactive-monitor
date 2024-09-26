import streamlit as st
import pandas as pd
import plotly.express as px

# Sample data for charts
df = pd.DataFrame({
    'Category': ['A', 'B', 'C'],
    'Value': [10, 20, 15]
})

# Function to display content based on button click
def display_content(button_name):
    if button_name == 'Button 1':
        st.markdown("## You clicked Button 1!")
        st.write("This is some text for Button 1.")
        fig = px.bar(df, x='Category', y='Value', title='Chart for Button 1')
        st.plotly_chart(fig)
    elif button_name == 'Button 2':
        st.markdown("## You clicked Button 2!")
        st.write("This is some different text for Button 2.")
        fig = px.pie(df, values='Value', names='Category', title='Chart for Button 2')
        st.plotly_chart(fig)
    elif button_name == 'Button 3':
        st.markdown("## You clicked Button 3!")
        st.write("And here's some more text for Button 3.")
        fig = px.line(df, x='Category', y='Value', title='Chart for Button 3')
        st.plotly_chart(fig)

# Create buttons with multi-line text
col1, col2, col3 = st.columns(3)
with col1:
    button1 = st.button("""
    **Button 1**
    This is a multi-line
    description for Button 1.
    """)
with col2:
    button2 = st.button("""
    **Button 2**
    This is another multi-line
    description for Button 2.
    """)
with col3:
    button3 = st.button("""
    **Button 3**
    And yet another multi-line
    description for Button 3.
    """)

# Display content based on button click
if button1:
    display_content('Button 1')
elif button2:
    display_content('Button 2')
elif button3:
    display_content('Button 3')
