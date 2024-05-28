# Halo Bot Training Data Analysis

## Descriptions

This project is designed to help **Halo Infinite** players improve their skills in competitive matches by analyzing training sessions against bots. Following [Shyway's advice](https://www.youtube.com/watch?v=_NJ-PJF9lrc&t=0s), I conduct training sessions against 8 ODST level bots in Free For All matches. The goal is to achieve the most kills in 15 minutes with the least deaths possible.

I use **Google Sheets** to manually log data from each training session, as these results are not automatically saved in the player's stats. The data is then analyzed in **Python** using libraries like **pandas** and **plotly** to generate charts and perform detailed analysis with **Gemini AI**.

## Contents

- **Data Extraction**: Connect to Google Sheets to retrieve training session data.
- **Chart Generation**: Visualize match statistics using plotly.
- **Data Analysis**: Use Gemini AI to analyze charts and provide advice to improve player skills.
- **User Interface**: Interactive interface built with Streamlit.

## Installation

1. **Clone the repository**:

    ```sh
    git clone https://github.com/yourusername/halo-bot-training-data.git
    cd halo-bot-training-data
    ```

2. **Create and activate a virtual environment**:

    ```sh
    python -m venv env
    source env/bin/activate  # On Windows use `env\Scripts\activate`
    ```

3. **Install dependencies**:

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
   - Create a `.env` file in the project root with the following variables:

    ```sh
    GOOGLE_AI_KEY=your_google_ai_key
    GOOGLE_JSON=your_google_service_account_json
    GOOGLE_SHEET=your_google_sheet_url
    ```

## Usage

1. **Run the application**:

    ```sh
    streamlit run app.py
    ```

2. **Update data**:
   - In the Streamlit interface, press the "Update Data" button to fetch the latest data from Google Sheets.

3. **Visualization and analysis**:
   - Browse through the generated charts and read the analyses provided by Gemini AI in both English and Spanish.

## Features

- **Data Extraction from Google Sheets**: Uses the Google API to fetch manually logged training data.
- **Chart Generation**: Visualizes key statistics such as kills, deaths, accuracy, damage dealt and taken, and K/D ratio.
- **Analysis with Gemini AI**: Provides detailed analysis of the generated charts and data, offering advice to improve player skills.
- **Multilingual Interface**: Supports both English and Spanish, making it easy to understand the generated analyses and charts.

## Main Code

### Google Sheets Connection and Data Extraction

```python
from google.oauth2 import service_account
import pandas as pd
import gspread
import json
import os
from dotenv import load_dotenv

def data_from_gsheets():
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
## Chart Generation with Plotly
```python
import plotly.graph_objects as go

def last_matches_plot(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Kills'], mode='lines+markers', name='Kills', line=dict(color='#FF2A6D')))
    fig.add_trace(go.Scatter(x=data['Date time'], y=data['Deaths'], mode='lines+markers', name='Deaths', line=dict(color='#05D9E8')))
    fig.update_layout(title='Last Games', hovermode='x', plot_bgcolor='#01012B', width=1200, height=660)
    return fig
```

## Analysis with Gemini AI
```python
import google.generativeai as genai
from PIL import Image
from io import BytesIO

genai.configure(api_key=os.getenv('GOOGLE_AI_KEY'))
img_model = genai.GenerativeModel('gemini-1.5-pro-latest')

def create_image_from_plot(plot):
    img_bytes = plot.to_image(format='png')
    img_data = BytesIO(img_bytes)
    img = Image.open(img_data)
    return img

def analyze_plot_spa(plot_function):
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
```

## Additional Features:

* Includes a user-friendly interface with tabs for English and Spanish analysis.
* Provides options to dynamically update the data and regenerate the analysis.

## Benefits:

* Objective and data-driven evaluation of player performance.
* Targeted recommendations for skill improvement.
* Enhanced understanding of game mechanics and player strengths/weaknesses.
* Improved decision-making and strategic planning during gameplay.
* Motivation and accountability for training efforts.

## Future updates:
* Use of player information on matches against humans to analyze the impacts of the training, the data will be extracted from Halo Infinite's Service Records

## Contributions
Contributions are welcome! Feel free to open an issue or submit a pull request to improve this project.