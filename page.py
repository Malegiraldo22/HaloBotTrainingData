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

def analyze_plot_spa(plot_function):
    """
    Function that takes a plot and uses Gemini Pro Vision to Analyze it

    Args:
        plot_function (Function): Function used to generate the plot

    Returns:
        str: Analysis generated by Gemini Pro Vision in spanish
    """
    temp_plot = create_image_from_plot(plot_function)
    promt = """
            Utiliza la gráfica y realiza un análisis de los datos que se muestran en ella, teniendo en cuenta el siguiente contexto:
            1. Los datos se generaron después de un partido de entrenamiento entre un humano y 8 bots en Halo Infinite, siguiendo las reglas de Halo Championship Series en una partida todos contra todos.
            2. El objetivo del entrenamiento es mejorar las habilidades del jugador.
            3. La gráfica contiene los resultados de todas las partidas jugadas hasta el momento.
            4. Ten en cuenta que las primeras 5 partidas se jugaron contra 4 bots en lugar de 8.
            5. Proporciona consejos al jugador para mejorar sus habilidades teniendo en cuenta los datos mostrados.
            Además, no calcules promedios para realizar el análisis.
            """
    response = img_model.generate_content([promt, temp_plot], stream=True)
    response.resolve()
    return response.text

#Plot generation functions
def last_matches_plot(data):
    """Function that generates a plot containing the results of the matches in the file

    Args:
        data (DataFrame): Dataframe that contains the information

    Returns:
        Plot: Plotly plot with the results of the match
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Kills'], mode='lines+markers', name='Kills', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Deaths'], mode='lines+markers', name='Deaths', line=dict(color='#05D9E8')))
    fig.update_layout(title='Last Games', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def shots_fired_plot(data):
    """Function that generates a plot containing the results of the matches in the file

    Args:
        data (DataFrame): Dataframe that contains the information

    Returns:
        Plot: Plotly plot with the amount of shots fired and shots hit
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Shots Fired'], mode='lines+markers', name='Shots Fired', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Shots Hit'], mode='lines+markers', name='Shots Hit', line=dict(color='#05D9E8')))
    fig.update_layout(title='Shooting', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def accuracy_plot(data):
    """Function that generates a plot containing the results of the matches in the file

    Args:
        data (DataFrame): Dataframe that contains the information

    Returns:
        Plot: Plotly plot with the accuracy results
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Accuracy'], mode='lines+markers', name='Accuracy', line=dict(color='#FF2A6D')))
    fig.update_layout(title='Accuracy (%)', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def damage_plot(data):
    """Function that generates a plot containing the results of the matches in the file

    Args:
        data (DataFrame): Dataframe that contains the information

    Returns:
        Plot: Plotly plot with damage dealt and damage taken
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Damage Dealt'], mode='lines+markers', name='Damage Dealt', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Damage Taken'], mode='lines+markers', name='Damage Taken', line=dict(color='#05D9E8')))
    fig.update_layout(title='Damage', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

def kd_ratio_plot(data):
    """Function that generates a plot containing the results of the matches in the file

    Args:
        data (DataFrame): Dataframe that contains the information

    Returns:
        Plot: Plotly plot with the K/D ratio for the player
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['K/D Ratio'], mode='lines+markers', name='K/D Ratio', line=dict(color='#FF2A6D')))
    fig.update_layout(title='K/D Ratio', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig

#Language selection
eng, spa = st.tabs(['English', 'Español'])

#English Version
with eng:
    st.title('Halo Bot Training Data')
    st.markdown("""
                Halo Infinite's Ranked Slayer test the players skill and weapon mastery. In order to improve the player must train, over and over. I decided to follow Shyway's [advice](https://www.youtube.com/watch?v=_NJ-PJF9lrc&t=0s) to do training sessions against 8 bots on ODST level in a Free For All battle. The idea is to do the most amount of kills in 15 minutes with the least amount of deaths. This should improve your aim and help you to react faster in a competitive match.
                As a way to follow my statistics, I built a spreadsheet on Google Sheets were I update the data manually as the training results are not saved on the player's data. Then the data is read in python and analyzed using pandas and plotly to generate plots.
                In this way I can follow my stats and see if I have improved in the training sessions. I used Gemini's API to analyze the plots and the data collected and generate advices to improve my skills. A later update to this app should include the data of competitive matches that I play to see if there is a real improvement in my skills.
    """)

    data = data_from_gsheets()

    if st.button('Update Data'):
        data = data_from_gsheets()

    #Plots
    st.subheader("Data Plots")
    st.markdown("""
                In this section I'll show plots that will allow to compare the statistics of each match played
                """)

    try:
        st.plotly_chart(last_matches_plot(data))
        st.markdown(analyze_plot(last_matches_plot(data)))
    except Exception as e:
        st.markdown("Couldn't Analyze the data")

    try:
        st.plotly_chart(shots_fired_plot(data))
        st.markdown(analyze_plot(shots_fired_plot(data)))
    except Exception as e:
        st.markdown("Couldn't analyze the data")

    try:
        st.plotly_chart(accuracy_plot(data))
        st.markdown(analyze_plot(accuracy_plot(data)))
    except Exception as e:
        st.markdown("Couldn't analyze the data")

    try:
        st.plotly_chart(damage_plot(data))
        st.markdown(analyze_plot(damage_plot(data)))
    except Exception as e:
        st.markdown("Couldn't analyze the data")

    try:
        st.plotly_chart(kd_ratio_plot(data))
        st.markdown(analyze_plot(kd_ratio_plot(data)))
    except Exception as e:
        st.markdown("Couldn't analyze the data")

    st.subheader("DataFrame")
    st.dataframe(data, hide_index=True, use_container_width=True)
    try:
        response = text_model.generate_content(f"""
        Use the following information: {data}, also consider that the training sessions used to generate the data are 8 bots against
        the player in a free for all match in Halo Infinite, following Halo Championship Series rules, and perform the following tasks:
        1. Perform a general analysis of the data.
        2. For each day calculate the average for each statistic, round the average values.
        3. Extract the dates with the best and worst results.
        4. Generate tips that can help the player improve their individually skills.
        5. Considering the results obtained, is there any correlation between the data?
        6. Can you assume what style of play the player uses and how could it improve individually?
        7. How should the player reduce its negative stats without altering the individual playstyle assumed in point 5?
        8. Based on point 6, What strategies can the player use within the game to overcome challenges and What resources are available outside the game that can help the player learn and grow?""")
        st.markdown(response.text)
    except Exception as e:
        st.markdown("Couldn't analyze the data")

with spa:
    st.title('Halo Bot Training Data')
    st.markdown("""
                El modo Ranked Slayer de Halo Infinite pone a prueba la habilidad y el dominio de las armas de los jugadores. Para mejorar, el jugador debe entrenar una y otra vez. Decidí seguir el [consejo](https://www.youtube.com/watch?v=_NJ-PJF9lrc&t=0s) de Shyway de realizar sesiones de entrenamiento contra 8 bots en nivel ODST en una batalla Todos contra todos. La idea es hacer la mayor cantidad de bajas en 15 minutos con la menor cantidad de muertes. Esto debería mejorar la puntería y ayudar a reaccionar más rápido en una partida competitiva.
                Como forma de seguir mis estadísticas, creé una hoja de cálculo en Google Sheets donde actualizo los datos manualmente, ya que los resultados del entrenamiento no se guardan en los datos del jugador. Luego, los datos se leen en Python y se analizan usando pandas y plotly para generar gráficos.
                De esta forma puedo seguir mis estadísticas y ver si he mejorado en los entrenamientos. Utilicé la API de Gemini para analizar los gráficos y los datos recopilados y generar consejos para mejorar mis habilidades. Una actualización posterior de esta aplicación debería incluir los datos de los partidos competitivos que juego para ver si hay una mejora real en mis habilidades.
    """)

    data = data_from_gsheets()

    if st.button('Actualizar datos'):
        data = data_from_gsheets()

    #Plots
    st.subheader("Data Plots")
    st.markdown("""
                En esta sección mostraré gráficos que permitirán comparar las estadísticas de cada partida.
                """)

    try:
        st.plotly_chart(last_matches_plot(data))
        st.markdown(analyze_plot_spa(last_matches_plot(data)))
    except Exception as e:
        st.markdown("No es posible analizar los datos")

    try:
        st.plotly_chart(shots_fired_plot(data))
        st.markdown(analyze_plot_spa(shots_fired_plot(data)))
    except Exception as e:
        st.markdown("No es posible analizar los datos")

    try:
        st.plotly_chart(accuracy_plot(data))
        st.markdown(analyze_plot_spa(accuracy_plot(data)))
    except Exception as e:
        st.markdown("No es posible analizar los datos")

    try:
        st.plotly_chart(damage_plot(data))
        st.markdown(analyze_plot_spa(damage_plot(data)))
    except Exception as e:
        st.markdown("No es posible analizar los datos")

    try:
        st.plotly_chart(kd_ratio_plot(data))
        st.markdown(analyze_plot_spa(kd_ratio_plot(data)))
    except Exception as e:
        st.markdown("No es posible analizar los datos")

    st.subheader("DataFrame")
    st.dataframe(data, hide_index=True, use_container_width=True)
    try:
        response = text_model.generate_content(f"""
        Utiliza la siguiente información: {data}. Ten en cuenta también que las sesiones de entrenamiento utilizadas para generar los datos son de 8 bots contra el jugador en una partida "todos contra todos" en Halo Infinite, siguiendo las reglas de la Halo Championship Series. Realiza las siguientes tareas:
        1. Realiza un análisis general de los datos.
        2. Para cada día calcula el promedio de las estadisticas, redondea los resultados.
        3. Extrae las fechas con los mejores y peores resultados.
        4. Genera consejos que puedan ayudar al jugador a mejorar sus habilidades individuales.
        5. Teniendo en cuenta los resultados obtenidos, ¿hay alguna correlación entre los datos?
        6. ¿Puedes suponer qué estilo de juego utiliza el jugador y cómo podría mejorar individualmente?
        7. ¿Cómo debería el jugador reducir sus estadísticas negativas sin alterar el estilo de juego individual asumido en el punto 5?
        8. Basado en el punto 6, ¿qué estrategias puede usar el jugador dentro del juego para superar desafíos? ¿Qué recursos están disponibles fuera del juego que pueden ayudar al jugador a aprender y crecer?""")
        st.markdown(response.text)
    except Exception as e:
        st.markdown("No es posible analizar los datos")