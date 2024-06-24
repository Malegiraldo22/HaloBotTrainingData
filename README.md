# Halo Bot Training Data Analysis

## Overview

Welcome to the **Halo Bot Training Data Analysis** project! This project is designed to help you track and analyze your training sessions in Halo Infinite's Ranked Slayer mode. By following Shyway's [advice](https://www.youtube.com/watch?v=_NJ-PJF9lrc&t=0s), you'll engage in training sessions against 8 bots at ODST level in a Free For All battle, aiming to improve your kills while minimizing deaths over 15 minutes.

This project leverages Google Sheets, Python, and powerful visualization tools to provide insightful data analysis and visualizations of your training performance.

## Features

- **Data Extraction**: Fetch training data directly from Google Sheets.
- **Data Analysis**: Utilize pandas and plotly to process and visualize your performance data.
- **Interactive Dashboards**: View interactive plots to track your progress over time.
- **AI Insights**: Get detailed analysis and improvement tips using Gemini AI.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following:

- Python 3.7 or later installed on your system.
- Access to Google Sheets API and Google Gemini API.
- A Google Sheets file with your training data.
- Environment variables set up for your Google API credentials.

### Installation

1. **Clone the Repository**:
    ```sh
    git clone https://github.com/Malegiraldo22/halo-bot-training-data.git
    cd halo-bot-training-data
    ```

2. **Install Dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Set Up Environment Variables**:
    Create a `.env` file in the project directory with the following content:
    ```env
    GOOGLE_JSON='your_google_service_account_json'
    GOOGLE_SHEET='your_google_sheet_url'
    GOOGLE_AI_KEY='your_google_ai_key'
    ```

### Usage
Run the Streamlit app to start analyzing your Halo trainig data:
```sh    
streamlit run page.py
```

## Detailed Description
### Data extraction from Google Sheets
The `data_from_gsheets` function extracts data from your Google Sheets File, and calculates de Kill/Death ratio to be used in the analysis

```python
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
```

## Plot Generation
The `generate_plots` function creates various plots to visualize your performance statistics such as kills, deaths, accuracy and damage deatl.
```python
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
```

## Interactive Dashboards With Streamlit
The streamlit app provides an interactive interface to visualize your data. It includes tabs for English and Spanish, catering to a broader audience
```python
eng, spa = st.tabs(['English', 'Español'])
with eng:
    st.title('Halo Bot Training Data')
    # Further code for English tab...
with spa:
    st.title('Datos de Entrenamiento con Bots en Halo')
    # Further code for Spanish tab...
```

## AI Analysis
Using Gemini AI, the app provides a detailed analysis of your performance and offers personalized tips for improvement

```python
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
```

## Benefits:

* Objective and data-driven evaluation of player performance.
* Targeted recommendations for skill improvement.
* Enhanced understanding of game mechanics and player strengths/weaknesses.
* Improved decision-making and strategic planning during gameplay.
* Motivation and accountability for training efforts.

## Future updates:
* **Competitive Match Data:** Use of player information on matches against humans to analyze the impacts of the training, the data will be extracted from Halo Infinite's Service Records
* **Enhanced AI Analysis:** Improve the AI analysis for more precise and actionable feedback using video replays

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request to improve this project or bug fixes.