# YouTube Data Harvesting and Warehousing using SQL and Streamlit

## Project Overview
This project is designed to build a Streamlit application that enables users to access, analyze, and manage data from multiple YouTube channels. The application interacts with the YouTube API to retrieve data, stores it in a SQL database, and provides a user-friendly interface to query and visualize the data.

## Features
 - YouTube Channel Data Retrieval: Input a YouTube channel ID to retrieve details such as channel name, subscriber count, total video count, playlist ID, video ID, likes, dislikes, and comments.
 - Data Collection: Collect data for up to 10 different YouTube channels and store it in a data lake with a single click.
 - SQL Database Integration: Option to store retrieved data in either MySQL or PostgreSQL.
 - Data Querying: Perform complex searches on the SQL database, including joining tables to retrieve detailed channel and video information.
 - Data Visualization: Display retrieved data and query results in a user-friendly format within the Streamlit app.

## App Link
Click On the [link](https://youtubedataharvestingandwarehousing-ex3vmitcezyqzazh8jjkqe.streamlit.app/) to visit the app
>[!NOTE]
In case the app is on sleep (Due to Lack of interaction) click wake up the app to re-start the app.
## Project Structure
`About.py`: Main Streamlit application file.
`.\pages\1_Add_Channel.py`: Page for Extracting Data by interacting with the `YouTube API`.
`.\pages\2_Library.py`: Page to Review stored data from the `SQL` database and update the Data base with `YouTube API`.
`.\pages\3_Analysis.py`: Page to Analaysie the database With Default Questions using SQL Queries.
`database.db`: `SQL` database to Save and Load Extracted Data.
`requirements.txt`: List of required Python libraries.

## Setup Instructions
Prerequisites
Python 3.7+
Streamlit
MySQL or SQLite
Google API Key with YouTube Data API access

## Installation
 1. **Clone the Repository:**

    bash code
    ```
    git clone https://github.com/yourusername/guvi-youtube-data-harvesting.git
    cd guvi-youtube-data-harvesting
    ```
 2. **Install Dependencies:**
    
    bash code
    ```
    pip install -r requirements.txt
    ```
 3. **Set Up Database:**
   
    - Install MySQL or PostgreSQL.
    - Create a new database and update connection settings in data_storage.py.
 4. **Run the Streamlit Application:**
    bash code
    ```
    streamlit run app.py
    ```

## Usage
 1. **Input YouTube Channel ID:** Enter the ID of a YouTube channel in the Streamlit app to retrieve data.
 2. **Collect Data:** Click the button to store data from up to 10 channels in the data lake.
 3. **Query Data:** Use various search options to retrieve and analyze data from the SQL database.
 4. **Visualize Data:** View results directly within the Streamlit interface.

## SQL Queries
**The following queries are available in the application:**

 1. Names of all videos and their corresponding channels.
 2. Channels with the most videos and their video counts.
 3. Top 10 most viewed videos and their channels.
 4. Comments count per video and corresponding video names.
 5. Videos with the highest likes and their corresponding channel names.
 6. Total likes and dislikes for each video.
 7. Total views for each channel and corresponding channel names.
 8. Channels with videos published in 2022.
 9. Average duration of all videos in each channel.
 10. Videos with the highest number of comments and their channels.

## Results
This project successfully creates a Streamlit application that leverages the Google API to extract YouTube channel data, stores it in a SQL database, and provides intuitive tools for data analysis and visualization.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request for any changes.

## License
This project is licensed under the MIT License.
