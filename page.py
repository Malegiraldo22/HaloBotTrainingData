#Import libraries
from google.oauth2 import service_account
import pandas as pd
import gspread
import json
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import textwrap
import google.generativeai as genai
from IPython.display import Markdown
from PIL import Image
from io import BytesIO

#Page title and page configuration
st.set_page_config(
    page_title='Halo Bot Training Data',
    layout='wide'
)

st.title('Halo Bot Training Data')
st.markdown("""
            Halo Infinite's Ranked Slayer test the players skill and weapon mastery. In order to improve the player must train, over and over. I decided to follow Shyway's [advice](https://www.youtube.com/watch?v=_NJ-PJF9lrc&t=0s) to do training sessions against 8 bots on ODST level in a Free For All battle. The idea is to do the most amount of kills in 15 minutes with the least amount of deaths. This should improve your aim and help you to react faster in a competitive match.
            As a way to follow my statistics, I built a spreadsheet on Google Sheets were I update the data manually as the training results are not saved on the player's data. Then the data is read in python and analyzed using pandas and plotly to generate plots.
            In this way I can follow my stats and see if I have improved in the training sessions. I used Gemini's API to analyze the plots and the data collected and generate advices to improve my skills. A later update to this app should include the data of competitive matches that I play to see if there is a real improvement in my skills.
""")

#Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_AI_KEY'))
text_model = genai.GenerativeModel('gemini-pro')
img_model = genai.GenerativeModel('gemini-pro-vision')


#Extracting the data from Google Sheets
def data_from_gsheets():
    """Function that extracts data from a google sheets file using google's api

    Returns:
        DataFrame: DataFrame with the info in the file
    """
    load_dotenv()
    google_json = os.getenv('GOOGLE_JSON')
    service_account_info = json.loads(google_json)
    credentials = service_account.Credentials.from_service_account_info(service_account_info)
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds_with_scope = credentials.with_scopes(scope)
    client = gspread.authorize(creds_with_scope)
    spreadsheet = client.open_by_url(os.getenv('GOOGLE_SHEET'))
    worksheet = spreadsheet.get_worksheet(0)
    records_data = worksheet.get_all_records()
    records_df = pd.DataFrame.from_dict(records_data)
    records_df['K/D Ratio'] = round(records_df.Kills / records_df.Deaths, 1)
    return records_df

data = data_from_gsheets()

if st.button('Update Data'):
    data = data_from_gsheets()


#Save temp plot
def create_image_from_plot(plot):
   """
   Creates a PIL Image object from a plot object without using temporary files.

   Args:
       plot: The plot object to convert to an image.

   Returns:
       The PIL Image object representing the plot.
   """

   img_bytes = plot.to_image(format='png')
   img_data = BytesIO(img_bytes)
   img = Image.open(img_data)
   return img

#Analyze plots
def analyze_plot(plot_function):
    """
    Function that takes a plot and uses Gemini Pro Vision to Analyze it

    Args:
        plot_function (Function): Function used to generate the plot

    Returns:
        str: Analysis generated by Gemini Pro Vision
    """
    temp_plot = create_image_from_plot(plot_function)
    promt = """
            Use the plot and make an analysis about the data shown in it, using the next context:
            1. The data is generated after a training match between a human and 8 bots in Halo infinite, following Halo Championship
            series rules in a free for all match
            2.  The focus of the training is to improve the skills of the player
            3. The plot contains the results of all matches played so far
            4. Have in mind that the first 5 matches were played against 4 bots instead of 8
            5. Give advices to the player to improve his skills considering the data shown
            Also, do not calculate averages to do the analysis
            """
    response = img_model.generate_content([promt, temp_plot], stream=True)
    response.resolve()
    return response.text

#Plots
st.subheader("Data Plots")
st.markdown("""
            In this section I'll show plots that will allow to compare the statistics of each match played
            """)

def last_matches_plot(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Kills'], mode='lines+markers', name='Kills', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Deaths'], mode='lines+markers', name='Deaths', line=dict(color='#05D9E8')))
    fig.update_layout(title='Last Games', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def shots_fired_plot(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Shots Fired'], mode='lines+markers', name='Shots Fired', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Shots Hit'], mode='lines+markers', name='Shots Hit', line=dict(color='#05D9E8')))
    fig.update_layout(title='Shooting', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def accuracy_plot(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Accuracy'], mode='lines+markers', name='Accuracy', line=dict(color='#FF2A6D')))
    fig.update_layout(title='Accuracy (%)', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def damage_plot(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Damage Dealt'], mode='lines+markers', name='Damage Dealt', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Damage Taken'], mode='lines+markers', name='Damage Taken', line=dict(color='#05D9E8')))
    fig.update_layout(title='Damage', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def kd_ratio_plot(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['K/D Ratio'], mode='lines+markers', name='K/D Ratio', line=dict(color='#FF2A6D')))
    fig.update_layout(title='K/D Ratio', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

st.plotly_chart(last_matches_plot(data))
st.markdown(analyze_plot(last_matches_plot(data)))

st.plotly_chart(shots_fired_plot(data))
st.markdown(analyze_plot(shots_fired_plot(data)))

st.plotly_chart(accuracy_plot(data))
st.markdown(analyze_plot(accuracy_plot(data)))

st.plotly_chart(damage_plot(data))
st.markdown(analyze_plot(damage_plot(data)))

try:
    st.plotly_chart(kd_ratio_plot(data))
    st.markdown(analyze_plot(kd_ratio_plot(data)))
except Exception as e:
    st.markdown("Couldn't analyze the data")

st.subheader("DataFrame")
st.dataframe(data, hide_index=True, use_container_width=True)
response = text_model.generate_content(f"""
Use the following information: {data}, also consider that the training sessions used to generate the data are 8 bots against
and the player in a free for all match in Halo Infinite, following Halo Championship Series rules, and perform the following tasks:
1. Perform a general analysis of the data.
2. Extract the dates with the best and worst results.
3. Generate tips that can help the player improve their individually skills.
4. Considering the results obtained, is there any correlation between the data?
5. Can you assume what style of play the player uses and how could it improve individually?
6. How should the player reduce its negative stats without altering the individual playstyle assumed in point 5?
7. Based on point 6, What strategies can the player use within the game to overcome challenges and What resources are available outside the game that can help the player learn and grow?""")
st.markdown(response.text)