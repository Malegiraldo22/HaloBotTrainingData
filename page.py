import time
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

#Page title and page configuration
st.set_page_config(
    page_title='Halo Bot Training Data',
    layout='wide'
)

#Gemini AI
genai.configure(api_key=os.getenv('GOOGLE_AI_KEY'))
text_model = genai.GenerativeModel('gemini-1.5-pro-latest')
img_model = genai.GenerativeModel('gemini-1.5-pro-latest')

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

#Plot generation functions
def generate_plots(data):
    """Function that generates a plot containing the results of the matches in the file

    Args:
        data (DataFrame): Dataframe that contains the information

    Returns:
        Plot: Plotly plot with the results of the match
    """
    last_games = go.Figure()
    last_games.add_trace(go.Scatter(x=data['Date time'], y=data['Kills'], mode='lines+markers', name='Kills', line=dict(color='#FF2A6D')))
    last_games.add_trace(go.Scatter(x=data['Date time'], y=data['Deaths'], mode='lines+markers', name='Deaths', line=dict(color='#05D9E8')))
    last_games.update_layout(title='Last Games', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660, yaxis=dict(showgrid=True))
    
    shots_fired = go.Figure()
    shots_fired.add_trace(go.Scatter(x=data['Date time'], y=data['Shots Fired'], mode='lines+markers', name='Shots Fired', line=dict(color='#FF2A6D')))
    shots_fired.add_trace(go.Scatter(x=data['Date time'], y=data['Shots Hit'], mode='lines+markers', name='Shots Hit', line=dict(color='#05D9E8')))
    shots_fired.update_layout(title='Shooting', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660, yaxis=dict(showgrid=True))

    accuracy = go.Figure()
    accuracy.add_trace(go.Scatter(x=data['Date time'], y=data['Accuracy'], mode='lines+markers', name='Accuracy', line=dict(color='#FF2A6D')))
    accuracy.update_layout(title='Accuracy (%)', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660, yaxis=dict(showgrid=True))

    damage = go.Figure()
    damage.add_trace(go.Scatter(x=data['Date time'], y=data['Damage Dealt'], mode='lines+markers', name='Damage Dealt', line=dict(color='#FF2A6D')))
    damage.add_trace(go.Scatter(x=data['Date time'], y=data['Damage Taken'], mode='lines+markers', name='Damage Taken', line=dict(color='#05D9E8')))
    damage.update_layout(title='Damage', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660, yaxis=dict(showgrid=True))

    kd = go.Figure()
    kd.add_trace(go.Scatter(x=data['Date time'], y=data['K/D Ratio'], mode='lines+markers', name='K/D Ratio', line=dict(color='#FF2A6D')))
    kd.update_layout(title='K/D Ratio', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660, yaxis=dict(showgrid=True))

    return last_games, shots_fired, accuracy, damage, kd

def stats_cal(data):
    """
    Function that calculates averages for each stat in the Datafrade

    Args:
        data (Dataframe): Dataframe with the data

    Returns:
        Variables with each average for each stat
    """
    avg_kills = data['Kills'].mean()
    avg_deaths = data['Deaths'].mean()
    avg_accuracy = data['Accuracy'].mean()
    avg_damage_dealt = data['Damage Dealt'].mean()
    avg_damage_taken = data['Damage Taken'].mean()
    avg_kd = data['Kills'].mean()

    return avg_kills, avg_deaths, avg_accuracy, avg_damage_dealt, avg_damage_taken, avg_kd

#Language selection
eng, spa = st.tabs(['English', 'Español'])
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

    avg_kills, avg_deaths, avg_accuracy, avg_damage_dealt, avg_damage_taken, avg_kd = stats_cal(data)

    cards_container = st.container()
    with cards_container:
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_kills_fig = go.Figure()
            avg_kills_fig.add_trace(go.Indicator(
                mode = "number",
                value = round(avg_kills, 0),
                title = {"text":"Average Kills<br><span style='font-size:0.8em'>"}
            ))

            avg_deaths_fig = go.Figure()
            avg_deaths_fig.add_trace(go.Indicator(
                mode = "number",
                value = round(avg_deaths, 0),
                title = {"text":"Average Deaths<br><span style='font-size:0.8em'>"}
            ))

            avg_kills_fig.update_layout(margin=dict(t=0,b=0), height=200)
            avg_deaths_fig.update_layout(margin=dict(t=0,b=0), height=200)

            st.plotly_chart(avg_kills_fig)
            st.plotly_chart(avg_deaths_fig)

        with col2:
            avg_accuracy_fig = go.Figure()
            avg_accuracy_fig.add_trace(go.Indicator(
                mode = "number",
                value = avg_accuracy,
                number = {"suffix":"%"},
                title = {"text":"Average Accuracy<br><span style='font-size:0.8em'>"}
            ))

            avg_kd_fig = go.Figure()
            avg_kd_fig.add_trace(go.Indicator(
                mode = "number",
                value = avg_kd,
                title = {"text":"Average Kill/Death Ratio<br><span style='font-size:0.8em'>"}
            ))

            avg_accuracy_fig.update_layout(margin=dict(t=0,b=0), height=200)
            avg_kd_fig.update_layout(margin=dict(t=0,b=0), height=200)

            st.plotly_chart(avg_accuracy_fig)
            st.plotly_chart(avg_kd_fig)

        with col3:
            avg_damage_dealt_fig = go.Figure()
            avg_damage_dealt_fig.add_trace(go.Indicator(
                mode = "number",
                value = avg_damage_dealt,
                title = {"text":"Average Damage Dealt<br><span style='font-size:0.8em'>"}
            ))

            avg_damage_taken_fig = go.Figure()
            avg_damage_taken_fig.add_trace(go.Indicator(
                mode = "number",
                value = avg_damage_taken,
                title = {"text":"Average Damage Taken<br><span style='font-size:0.8em'>"}
            ))

            avg_damage_dealt_fig.update_layout(margin=dict(t=0,b=0), height=200)
            avg_damage_taken_fig.update_layout(margin=dict(t=0,b=0), height=200)

            st.plotly_chart(avg_damage_dealt_fig)
            st.plotly_chart(avg_damage_taken_fig)

    #Plots
    st.subheader("Data Plots")
    
    last_games, shots_fired, accuracy, damage, kd = generate_plots(data)

    plots_container = st.container()
    with plots_container:
        col1, col2 = st.columns(2)

        with col1:
            st.plotly_chart(last_games)
            st.plotly_chart(shots_fired)
            st.plotly_chart(accuracy)
        
        with col2:
            st.plotly_chart(damage)
            st.plotly_chart(kd)

    st.subheader("DataFrame")
    st.dataframe(data, hide_index=True, use_container_width=True)

    try:
        print("analyzing data...")
        response = text_model.generate_content(f"""
        You are a videogame coach speciallized in Halo Infinite at competitive level, use the following information: 
        {data} and plots {last_games}, {shots_fired}, {accuracy}, {damage}, {kd} to analyze the player. 
        Also consider that the training sessions used to generate the data are 8 bots against the player in a free for all match in Halo Infinite, 
        following Halo Championship Series rules, and perform the following tasks:
        1. Perform a detailed analysis of the data.
        2. Perform a long and detailed analysis for each plot: {last_games}, {shots_fired}, {accuracy}, {damage}, {kd}
        3. For each day calculate the average for each statistic, round the average values. Use {data} to make the calculations, show a summary instead of a table
        4. Extract the dates with the best and worst results. Use the dataframe {data} and show a summary instead of a table
        5. Generate tips that can help the player improve their individually skills.
        6. Considering the results obtained, is there any correlation between the data?
        7. Can you assume what style of play the player uses and how could it improve individually?
        8. How should the player reduce its negative stats without altering the individual playstyle assumed in point 5?
        9. Based on point 6, What strategies can the player use within the game to overcome challenges and What resources are available outside the game that can help the player learn and grow?
        10. Make a final thoughts where you present a full analysis of the data and plots and give your final conclusions
        """)
        st.markdown(response.text)
    except Exception as e:
        st.markdown("Couldn't analyze the data")
        print("Error: can't analyze data")

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

        avg_kills, avg_deaths, avg_accuracy, avg_damage_dealt, avg_damage_taken, avg_kd = stats_cal(data)

        cards_container = st.container()
        with cards_container:
            col1, col2, col3 = st.columns(3)
            with col1:
                avg_kills_fig = go.Figure()
                avg_kills_fig.add_trace(go.Indicator(
                    mode = "number",
                    value = round(avg_kills,0),
                    title = {"text":"Promedio de Asesinatos<br><span style='font-size:0.8em'>"}
                ))

                avg_deaths_fig = go.Figure()
                avg_deaths_fig.add_trace(go.Indicator(
                    mode = "number",
                    value = round(avg_deaths,0),
                    title = {"text":"Promedio de Muertes<br><span style='font-size:0.8em'>"}
                ))

                avg_kills_fig.update_layout(margin=dict(t=0,b=0), height=200)
                avg_deaths_fig.update_layout(margin=dict(t=0,b=0), height=200)

                st.plotly_chart(avg_kills_fig)
                st.plotly_chart(avg_deaths_fig)

            with col2:
                avg_accuracy_fig = go.Figure()
                avg_accuracy_fig.add_trace(go.Indicator(
                    mode = "number",
                    value = avg_accuracy,
                    number = {"suffix":"%"},
                    title = {"text":"Precisión Promedio<br><span style='font-size:0.8em'>"}
                ))

                avg_kd_fig = go.Figure()
                avg_kd_fig.add_trace(go.Indicator(
                    mode = "number",
                    value = avg_kd,
                    title = {"text":"Asesinatos/Muertes promedio<br><span style='font-size:0.8em'>"}
                ))

                avg_accuracy_fig.update_layout(margin=dict(t=0,b=0), height=200)
                avg_kd_fig.update_layout(margin=dict(t=0,b=0), height=200)

                st.plotly_chart(avg_accuracy_fig)
                st.plotly_chart(avg_kd_fig)

            with col3:
                avg_damage_dealt_fig = go.Figure()
                avg_damage_dealt_fig.add_trace(go.Indicator(
                    mode = "number",
                    value = avg_damage_dealt,
                    title = {"text":"Promedio Daño Infligido<br><span style='font-size:0.8em'>"}
                ))

                avg_damage_taken_fig = go.Figure()
                avg_damage_taken_fig.add_trace(go.Indicator(
                    mode = "number",
                    value = avg_damage_taken,
                    title = {"text":"Promedio Daño Recibido<br><span style='font-size:0.8em'>"}
                ))

                avg_damage_dealt_fig.update_layout(margin=dict(t=0,b=0), height=200)
                avg_damage_taken_fig.update_layout(margin=dict(t=0,b=0), height=200)

                st.plotly_chart(avg_damage_dealt_fig)
                st.plotly_chart(avg_damage_taken_fig)

        #Plots
        st.subheader("Data Plots")

        last_games, shots_fired, accuracy, damage, kd = generate_plots(data)

        plots_container = st.container()
        with plots_container:
            col1, col2 = st.columns(2)

            with col1:
                st.plotly_chart(last_games)
                st.plotly_chart(shots_fired)
                st.plotly_chart(accuracy)
            
            with col2:
                st.plotly_chart(damage)
                st.plotly_chart(kd)
        
        st.subheader("DataFrame")
        st.dataframe(data, hide_index=True, use_container_width=True)
        
        try:
            print("Esperando análisis...")
            time.sleep(15)
            print('Analizando datos...')
            response = text_model.generate_content(f"""
            Eres un entrenador de videojuegos especializado en Halo Infinite a nivel competitivo. Usa la siguiente información:
            {data} y gráficos {last_games}, {shots_fired}, {accuracy}, {damage}, {kd} para analizar al jugador.
            Además, considera que las sesiones de entrenamiento utilizadas para generar los datos son 8 bots contra el jugador en una partida libre para todos en Halo Infinite,
            siguiendo las reglas de la Serie de Campeonatos de Halo, y realiza las siguientes tareas:
            1. Realiza un análisis detallado de los datos.
            2. Realiza un análisis largo y detallado de cada gráfico: {last_games}, {shots_fired}, {accuracy}, {damage}, {kd}.
            3. Para cada día, calcula el promedio de cada estadística y redondea los valores promedio. Usa {data} para hacer los cálculos. Escribe un resumen en vez de mostrar una tabla con los resultados
            4. Extrae las fechas con los mejores y peores resultados. Usa el dataframe {data}. Escribe un resumen en vez de mostrar una tabla con los resultados
            5. Genera consejos que puedan ayudar al jugador a mejorar sus habilidades individuales.
            6. Considerando los resultados obtenidos, ¿existe alguna correlación entre los datos?
            7. ¿Puedes asumir qué estilo de juego utiliza el jugador y cómo podría mejorar individualmente?
            8. ¿Cómo debería el jugador reducir sus estadísticas negativas sin alterar el estilo de juego individual asumido en el punto 5?
            9. Basado en el punto 6, ¿Qué estrategias puede usar el jugador dentro del juego para superar desafíos y qué recursos están disponibles fuera del juego que pueden ayudar al jugador a aprender y crecer?
            10. 10. Haz un apartado de reflexiones finales donde presentes un análisis completo de los datos y gráficos, y da tus conclusiones finales
            """)
            st.markdown(response.text)
        except Exception as e:
            print("Error al analizar datos")
            st.markdown("No he podido analizar los datos")