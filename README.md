# HaloBotTrainingData

Description:

This project analyzes data generated after a Halo Infinite free-for-all slayer game in training mode played against 8 bots. The data is used to identify areas for improvement in the player's skills and to provide recommendations for targeted practice.

Author: Alejandro Giraldo

Features:

Data Extraction:

Retrieves data from a Google Sheets file using the Google Sheets API.

Data Analysis:

* Utilizes Pandas for data manipulation and Plotly for interactive visualizations.
* Generates various plots to illustrate key metrics such as kills, deaths, accuracy, damage dealt/taken, and K/D ratio.
* Automates data analysis using Google's Gemini AI for both text and image-based insights:
  * Provides a comprehensive analysis of the data.
  * Identifies dates with the best and worst results.
  * Generates tips for individual skill improvement.
  * Explores correlations within the data.
  * Suggests strategies for overcoming challenges within the game.
  * Recommends external resources for player development.

Additional Features:

* Includes a user-friendly interface with tabs for English and Spanish analysis.
* Provides options to dynamically update the data and regenerate the analysis.

Benefits:

* Objective and data-driven evaluation of player performance.
* Targeted recommendations for skill improvement.
* Enhanced understanding of game mechanics and player strengths/weaknesses.
* Improved decision-making and strategic planning during gameplay.
* Motivation and accountability for training efforts.

Usage:
* Obtain Data: Export training game data to a Google Sheets file.
* Configure API Keys: Obtain and set the API keys for the Google Sheets and Gemini AI services in the code.
* Run the Code: Execute the Python script to perform data analysis and generate insights.
* Review Analysis: Navigate through the interactive dashboard to view the plots, analysis, and recommendations.
* Apply Insights: Implement suggested strategies and techniques to enhance player performance.


Future updates:
* Use of player information on matches against humans to analyze the impacts of the training, the data will be extracted from Halo Infinite's Service Records