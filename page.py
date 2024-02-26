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

#Page title and page configuration
st.set_page_config(
    page_title='Halo Bot Training Data',
    layout='wide'
)

st.title('Halo Bot Training Data')
st.markdown("""
            Halo Infinite's Ranked Slayer test the players skill and weapon mastery. In order to improve the player must train, over and over. I decided to follow Shyway's [advice](https://www.youtube.com/watch?v=_NJ-PJF9lrc&t=0s) to do training sessions against 8 bots on ODST level in a Free For All battle. The idea is to do the most amount of kills in 15 minutes with the least amount of deaths. This should improve your aim and help you to react faster in a competitive match.
            As a way to follow my statistics, I built a spreadsheet on Google Sheets were I update the data manually as the training results are not saved on the player's data. Then the data is read in python and analyzed using pandas and plotly to generate plots.
            In this way I can follow my stats and see if I have improved in the training sessions. A later update to this app should include the data of competitive matches that I play to see if there is a real improvement in my skills.
""")

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

#Plots
st.subheader("Data Plots")
st.markdown("""
            In this section I'll show plots that will allow to compare the statistics of each match played
            """)

def last_matchs_plot(data):
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

st.plotly_chart(last_matchs_plot(data))
st.plotly_chart(shots_fired_plot(data))
st.plotly_chart(accuracy_plot(data))
st.plotly_chart(damage_plot(data))
st.plotly_chart(kd_ratio_plot(data))

st.subheader("DataFrame")
st.dataframe(data, hide_index=True, use_container_width=True)