# 📊 YouTube Advanced Analytics Dashboard �

🔗 **Live Demo**: [Try the Dashboard Here](https://youtube-analyzer-with-app-cpnmdvm6ky5mmaxaz98c9t.streamlit.app/)  


This Streamlit-based web application provides powerful data visualizations and advanced insights for any YouTube channel. It uses the YouTube Data API v3 to fetch channel and video data, then displays interactive charts and statistics for comprehensive performance analysis.

------------------------------------------------------------
Features
------------------------------------------------------------
- Real-time YouTube data fetching using the YouTube Data API v3
- Sidebar filters for date range, category, and minimum view count
- Channel overview showing subscribers, views, total videos, and playlists
- Interactive visualizations including:
  • Uploads per month
  • Top videos by views and likes
  • Views and likes over time
  • Likes heatmap by hour and day
  • Comments sunburst by category
  • Histogram of views by year
  • Scatter plot of likes vs duration
  • Cumulative likes and views growth
  • Calendar-style uploads per day
- Dark theme custom styling
- Faster reloads with Streamlit caching

------------------------------------------------------------
Technology Stack
------------------------------------------------------------
Frontend: Streamlit
API: YouTube Data API v3
Data Handling: Pandas, NumPy
Charts and Graphs: Plotly Express, Matplotlib
Utilities: isodate (for video duration parsing)

------------------------------------------------------------
Installation and Setup
------------------------------------------------------------
1. Requirements
   - Python 3.8 or higher
   - A valid YouTube Data API key

2. Install dependencies
   Run this command in your terminal:
       pip install streamlit google-api-python-client pandas numpy plotly matplotlib isodate

3. Add your YouTube API key
   In the code, locate:
       API_KEY = "YOUR_API_KEY"
   Replace "YOUR_API_KEY" with your actual API key from Google Cloud Console.

------------------------------------------------------------
Running the Dashboard
------------------------------------------------------------
1. Start the app:
       streamlit run app.py

2. Open your web browser and visit:
       http://localhost:8501/

3. Paste a valid YouTube Channel ID in the sidebar.
   You can also enable filters such as date range, categories, or minimum views.

------------------------------------------------------------
Project Structure
------------------------------------------------------------
YouTube-Advanced-Dashboard/
│
├── app.py               Main Streamlit application
├── requirements.txt     Dependencies list
└── README.txt           Project documentation

------------------------------------------------------------
API Quota Notes
------------------------------------------------------------
Each call to the YouTube API consumes quota units. Large requests or frequent refreshes may lead to quota exhaustion. Use within reasonable limits.

------------------------------------------------------------
License
------------------------------------------------------------
This project is licensed under the MIT License. For educational and analytical purposes only.

------------------------------------------------------------
Author
------------------------------------------------------------
Developed by [Your Name]
Date: October 2025
