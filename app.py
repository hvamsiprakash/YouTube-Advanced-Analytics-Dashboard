
# import streamlit as st
# from googleapiclient.discovery import build
# import pandas as pd
# import numpy as np
# import plotly.express as px
# import matplotlib.pyplot as plt
# import isodate

# API_KEY = "AIzaSyDz8r5kvSnlkdQTyeEMS4hn0EMpXfUV1ig"

# st.set_page_config(
#     page_title="YouTube Advanced Dashboard",
#     layout="wide",
#     page_icon="🎥",
#     initial_sidebar_state="auto"
# )

# # --- Custom Theme ---
# st.markdown("""
#     <style>
#     .stApp { background-color: #111 !important; }
#     div[data-testid="stMetricValue"], div[data-testid="stMetricLabel"] { color: #fff !important; }
#     h1, h2, h3, h4, h5, h6, .css-1v0mbdj, .css-1cpxqw2, .css-18ni7ap { color: #fff !important; }
#     .stTable, .stDataFrame, .stMarkdown, .stCaption { color: #fff !important; }
#     .stPlotlyChart { background-color: #222 !important;}
#     [data-testid="stSidebar"] { background-color: #1B1B1B !important; }
#     .css-1dp5vir { background-color: #111 !important; }
#     </style>
# """, unsafe_allow_html=True)

# sidebar = st.sidebar
# sidebar.title("Channel Insights & Filters")
# channel_id = sidebar.text_input("YouTube Channel ID", help="Paste your Channel ID here")
# date_filter = sidebar.checkbox("Enable Date Range Filter")
# category_filter = sidebar.multiselect(
#     "Filter by category", 
#     ["Film", "Autos", "Music", "Sports", "Gaming", "Comedy", "Entertainment", "News", "Howto", "Education", "Science", "Other"], 
#     default=["Film", "Autos", "Music", "Sports", "Gaming", "Comedy", "Entertainment", "News", "Howto", "Education", "Science", "Other"]
# )
# min_views = sidebar.number_input("Minimum Views (global filter)", min_value=0, value=0, step=100)

# def get_youtube_client():
#     return build("youtube", "v3", developerKey=API_KEY)

# @st.cache_data(ttl=1800)
# def fetch_channel(channel_id):
#     yt = get_youtube_client()
#     req = yt.channels().list(part="snippet,statistics,contentDetails", id=channel_id)
#     res = req.execute()
#     if res["items"]:
#         return res["items"][0]
#     else:
#         return None

# @st.cache_data(ttl=1800)
# def fetch_all_videos(uploads_playlist_id, max_results=300):
#     yt = get_youtube_client()
#     videos = []
#     nextPageToken = None
#     while len(videos) < max_results:
#         req = yt.playlistItems().list(
#             part="snippet,contentDetails",
#             playlistId=uploads_playlist_id,
#             maxResults=min(50, max_results - len(videos)),
#             pageToken=nextPageToken
#         )
#         res = req.execute()
#         videos += res["items"]
#         nextPageToken = res.get("nextPageToken")
#         if not nextPageToken:
#             break
#     return [item["contentDetails"]["videoId"] for item in videos]

# @st.cache_data(ttl=1800)
# def fetch_video_details(video_ids):
#     if not video_ids: return pd.DataFrame()
#     yt = get_youtube_client()
#     all_video = []
#     for start in range(0, len(video_ids), 50):
#         req = yt.videos().list(
#             part="snippet,statistics,contentDetails",
#             id=",".join(video_ids[start:start+50])
#         )
#         res = req.execute()
#         for item in res["items"]:
#             stats = item.get("statistics", {})
#             snippet = item.get("snippet", {})
#             content = item.get("contentDetails", {})
#             all_video.append({
#                 "Video ID": item["id"],
#                 "Title": snippet.get("title", ""),
#                 "PublishedAt": snippet.get("publishedAt", ""),
#                 "Views": int(stats.get("viewCount", 0)),
#                 "Likes": int(stats.get("likeCount", 0)),
#                 "Comments": int(stats.get("commentCount", 0)),
#                 "Tags": snippet.get("tags", []),
#                 "CategoryId": snippet.get("categoryId", ""),
#                 "Duration": content.get("duration", "")
#             })
#     return pd.DataFrame(all_video)

# @st.cache_data(ttl=1800)
# def fetch_playlists(channel_id):
#     yt = get_youtube_client()
#     playlists = []
#     nextPageToken = None
#     while True:
#         req = yt.playlists().list(part="snippet,contentDetails", channelId=channel_id, maxResults=50, pageToken=nextPageToken)
#         res = req.execute()
#         playlists.extend(res["items"])
#         nextPageToken = res.get("nextPageToken")
#         if not nextPageToken:
#             break
#     return playlists

# def parse_duration(duration):
#     try:
#         td = isodate.parse_duration(duration)
#         return td.total_seconds() / 60  # minutes
#     except:
#         return 0

# category_map = {
#     "1": "Film", "2": "Autos", "10": "Music", "17": "Sports", "20": "Gaming", "23": "Comedy",
#     "24": "Entertainment", "25": "News", "26": "Howto", "27": "Education", "28": "Science"
# }

# if channel_id:
#     channel = fetch_channel(channel_id)
#     if not channel:
#         st.error("Channel not found. Check your Channel ID and quota.")
#     else:
#         uploads_pid = channel["contentDetails"]["relatedPlaylists"]["uploads"]
#         video_ids = fetch_all_videos(uploads_pid, max_results=300)
#         df_vid = fetch_video_details(video_ids)
#         playlists = fetch_playlists(channel_id)

#         # Preprocessing
#         df_vid["DurationMin"] = df_vid["Duration"].map(parse_duration)
#         df_vid["PublishedDate"] = pd.to_datetime(df_vid["PublishedAt"], errors='coerce')
#         df_vid["Month"] = df_vid["PublishedDate"].dt.strftime("%Y-%m")
#         df_vid["DayOfWeek"] = df_vid["PublishedDate"].dt.day_name()
#         df_vid["Year"] = df_vid["PublishedDate"].dt.year
#         df_vid["Day"] = df_vid["PublishedDate"].dt.day
#         df_vid["Hour"] = df_vid["PublishedDate"].dt.hour
#         df_vid["Category"] = df_vid["CategoryId"].map(lambda x: category_map.get(x, "Other"))

#         if date_filter and not df_vid.empty:
#             min_date, max_date = df_vid["PublishedDate"].min().date(), df_vid["PublishedDate"].max().date()
#             start_date = sidebar.date_input("Start Date", min_value=min_date, max_value=max_date, value=min_date)
#             end_date = sidebar.date_input("End Date", min_value=min_date, max_value=max_date, value=max_date)
#             df_vid = df_vid[(df_vid["PublishedDate"].dt.date >= start_date) & (df_vid["PublishedDate"].dt.date <= end_date)]

#         # Apply global filters
#         df_vid = df_vid[df_vid["Category"].isin(category_filter)]
#         df_vid = df_vid[df_vid["Views"] >= min_views]

#         st.markdown(f"# Insights for: **{channel['snippet']['title']}**")
#         st.markdown("## Channel Overview")
#         cards = st.columns(5)
#         with cards[0]:
#             st.image(channel["snippet"]["thumbnails"]["high"]["url"], width=80)
#         with cards[1]:
#             st.metric("Subscribers", f"{int(channel['statistics']['subscriberCount']):,}")
#         with cards[2]:
#             st.metric("Total Views", f"{int(channel['statistics']['viewCount']):,}")
#         with cards[3]:
#             st.metric("Total Videos", f"{int(channel['statistics']['videoCount']):,}")
#         if playlists:
#             with cards[4]:
#                 st.metric("Total Playlists", f"{len(playlists):,}")
#         st.markdown(f"**Channel Description:** {channel['snippet'].get('description','No description')}")
#         if not df_vid.empty:
#             st.markdown("Uploads Per Month")
#             up_month = df_vid["Month"].value_counts().sort_index()
#             fig = px.bar(x=up_month.index, y=up_month.values, labels={'x':"Month",'y':'Uploads'}, color=up_month.values, color_continuous_scale='reds', title="Uploads per Month")
#             st.plotly_chart(fig, use_container_width=True)

#             st.markdown("Top Videos by Views")
#             top_vids = df_vid.sort_values("Views", ascending=False).head(10)
#             fig = px.bar(top_vids, x="Views", y="Title", orientation='h', color="Views", color_continuous_scale='reds', title="Top Videos by Views")
#             st.plotly_chart(fig, use_container_width=True)

#             st.markdown("Top Videos by Likes")
#             top_likes = df_vid.sort_values("Likes", ascending=False).head(10)
#             fig = px.bar(top_likes, x="Title", y="Likes", color="Likes", color_continuous_scale='reds', title="Top Videos by Likes")
#             st.plotly_chart(fig, use_container_width=True)

#             st.markdown("Views & Likes Over Time")
#             grouped = df_vid.groupby("Month")[["Views", "Likes"]].sum().reset_index()
#             fig = px.line(grouped, x="Month", y=["Views", "Likes"], markers=True, color_discrete_sequence=['firebrick', 'indianred'])
#             st.plotly_chart(fig, use_container_width=True)

#             # Advanced Replacement: Heatmap of Likes by Hour and Day
#             st.markdown("Heatmap: Likes by Hour and Day")
#             likes_heatmap_data = df_vid.groupby(["DayOfWeek", "Hour"])["Likes"].sum().unstack(fill_value=0)
#             hour_col, chart_col = st.columns([1,5])
#             with hour_col:
#                 selected_hour = st.selectbox("Filter Hour", sorted(df_vid["Hour"].unique()), key="likes_heat_hour")
#             with chart_col:
#                 likes_filtered = likes_heatmap_data.loc[:, selected_hour:selected_hour]
#                 fig = px.imshow(likes_filtered, color_continuous_scale="reds", title=f"Likes Heatmap (Hour={selected_hour})")
#                 st.plotly_chart(fig, use_container_width=True)

#             # Advanced Replacement: Category sunburst by comments
#             st.markdown("Sunburst of Comments by Category/Video")
#             filter_cat = st.selectbox("Filter category", sorted(df_vid["Category"].unique()), key="sunburst_cat")
#             sunburst_df = df_vid[df_vid["Category"] == filter_cat][["Category", "Title", "Comments"]]
#             fig = px.sunburst(sunburst_df, path=["Category", "Title"], values="Comments", color="Comments", color_continuous_scale="reds", title="Comments Sunburst")
#             st.plotly_chart(fig, use_container_width=True)

#             # Advanced Replacement: Histogram views by selected year
#             st.markdown("Histogram of Views by Year")
#             year_col, chart_col = st.columns([1,5])
#             with year_col:
#                 select_year = st.selectbox("Choose year", sorted(df_vid["Year"].unique()), key="hist_year")
#             views_year_df = df_vid[df_vid["Year"] == select_year]
#             with chart_col:
#                 fig = px.histogram(views_year_df, x="Views", nbins=15, color_discrete_sequence=['red'], title=f"Views Distribution ({select_year})")
#                 st.plotly_chart(fig, use_container_width=True)

#             # Advanced Replacement: Scatterplot Likes vs Duration for selected category
#             st.markdown("Scatterplot Likes vs Duration (Category)")
#             cat_col, chart_col = st.columns([1,5])
#             with cat_col:
#                 selected_cat = st.selectbox("Scatter Category", sorted(df_vid["Category"].unique()), key="scatter_likes_cat")
#             filtered_df = df_vid[df_vid["Category"] == selected_cat]
#             with chart_col:
#                 fig = px.scatter(filtered_df, x="DurationMin", y="Likes", color="Likes", color_continuous_scale='reds', size="Comments", hover_name="Title", title=f"Likes vs Duration ({selected_cat})")
#                 st.plotly_chart(fig, use_container_width=True)

#             # Advanced Replacement: Line chart for Likes Cumulative over Date, with filter for min likes
#             st.markdown("Likes Cumulative Growth (Min Likes Filter)")
#             likes_min_col, chart_col = st.columns([1,5])
#             with likes_min_col:
#                 min_likes_for_line = st.slider("Minimum Likes", min_value=int(df_vid["Likes"].min()), max_value=int(df_vid["Likes"].max()), value=0, key="min_likes_cum")
#             likes_cum_df = df_vid[df_vid["Likes"] >= min_likes_for_line].sort_values("PublishedDate")
#             likes_cum_df["CumulativeLikes"] = likes_cum_df["Likes"].cumsum()
#             with chart_col:
#                 fig = px.line(likes_cum_df, x="PublishedDate", y="CumulativeLikes", color_discrete_sequence=["red"], title="Cumulative Likes Growth")
#                 st.plotly_chart(fig, use_container_width=True)

#             # Playlists Table
#             st.markdown("Playlists")
#             pl = pd.DataFrame([{
#                 "Title": p["snippet"]["title"],
#                 "VideoCount": p["contentDetails"].get("itemCount", "N/A")
#             } for p in playlists])
#             st.dataframe(pl)

#             # Most Engaged Videos Table
#             st.markdown("Most Engaged Videos")
#             most_engaged = df_vid.assign(TotalEngagement=lambda x: x["Likes"] + x["Comments"])
#             st.dataframe(most_engaged.sort_values("TotalEngagement", ascending=False)[
#                 ["Title", "TotalEngagement", "Likes", "Comments", "Views", "PublishedDate"]
#             ].head(10))

#             # Cumulative Views Growth
#             st.markdown("Cumulative Views Growth Over Time")
#             growth_df = df_vid.sort_values("PublishedDate")
#             growth_df["CumulativeViews"] = growth_df["Views"].cumsum()
#             fig = px.area(growth_df, x="PublishedDate", y="CumulativeViews", color_discrete_sequence=["red"], title="Cumulative Views Growth Over Time")
#             st.plotly_chart(fig, use_container_width=True)

#             # Videos per Day (Calendar-style scatter)
#             st.markdown("Videos per Day")
#             calendar_df = df_vid.groupby(df_vid["PublishedDate"].dt.date).size().reset_index(name="Uploads")
#             calendar_col, chart_col = st.columns([1,5])
#             with calendar_col:
#                 min_uploads = st.slider("Min uploads/day", min_value=1, max_value=int(calendar_df["Uploads"].max()), value=1, key="min_uploads_cal")
#             calendar_df = calendar_df[calendar_df["Uploads"] >= min_uploads]
#             with chart_col:
#                 fig = px.scatter(calendar_df, x="PublishedDate", y="Uploads", color="Uploads", color_continuous_scale="reds", title="Uploads per Day")
#                 st.plotly_chart(fig, use_container_width=True)
#         else:
#             st.warning("No video data found for this channel.")

#     sidebar.caption("YouTube style • Red charts • Advanced insights • Filters in sidebar")
# else:
#     st.info("Enter a valid YouTube Channel ID to see insights.")


 import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import isodate
from collections import Counter
import re
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings("ignore")

API_KEY = "AIzaSyDz8r5kvSnlkdQTyeEMS4hn0EMpXfUV1ig"

st.set_page_config(
    page_title="YT DeepDive — Channel Intelligence",
    layout="wide",
    page_icon="▶",
    initial_sidebar_state="expanded"
)

# ─── GLOBAL THEME ────────────────────────────────────────────────────────────
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
/* ── Base ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, .stApp { background: #0a0a0a !important; color: #e8e8e8 !important; font-family: 'DM Sans', sans-serif !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f0f 0%, #0a0a0a 100%) !important;
    border-right: 1px solid #1f1f1f !important;
}
[data-testid="stSidebar"] * { color: #ccc !important; }
[data-testid="stSidebar"] .stTextInput > div > div > input {
    background: #1a1a1a !important; border: 1px solid #333 !important; color: #fff !important;
    border-radius: 6px !important;
}

/* ── Main background ── */
[data-testid="stAppViewContainer"] > .main { background: #0a0a0a !important; }
[data-testid="block-container"] { padding: 1.5rem 2rem !important; }

/* ── Section header ── */
.section-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    letter-spacing: 3px;
    color: #ff0000;
    text-transform: uppercase;
    margin: 2.5rem 0 0.2rem 0;
    padding-left: 14px;
    border-left: 4px solid #ff0000;
    line-height: 1;
}
.section-sub {
    font-size: 0.78rem;
    color: #666;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
    padding-left: 18px;
}

/* ── Hero banner ── */
.hero-banner {
    background: linear-gradient(135deg, #0f0f0f 0%, #1a0000 50%, #0f0f0f 100%);
    border: 1px solid #2a0000;
    border-radius: 12px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-banner::before {
    content: '▶';
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 8rem;
    color: #1a0000;
    font-weight: bold;
}
.hero-channel-name {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.5rem;
    letter-spacing: 4px;
    color: #fff;
    margin: 0;
    line-height: 1;
}
.hero-handle {
    color: #ff0000;
    font-size: 0.9rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-top: 4px;
}

/* ── KPI Cards ── */
.kpi-card {
    background: #111;
    border: 1px solid #222;
    border-radius: 10px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    transition: border-color 0.2s, transform 0.2s;
    position: relative;
    overflow: hidden;
}
.kpi-card:hover { border-color: #ff0000; transform: translateY(-2px); }
.kpi-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #ff0000, transparent);
    opacity: 0;
    transition: opacity 0.2s;
}
.kpi-card:hover::after { opacity: 1; }
.kpi-label { font-size: 0.65rem; letter-spacing: 2px; color: #555; text-transform: uppercase; margin-bottom: 6px; }
.kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.2rem; color: #fff; letter-spacing: 2px; line-height: 1; }
.kpi-delta { font-size: 0.72rem; color: #ff4444; margin-top: 4px; font-family: 'JetBrains Mono', monospace; }

/* ── Insight Cards ── */
.insight-card {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 10px;
    padding: 1.4rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.insight-card:hover { border-color: #333; }
.insight-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3rem;
    color: #1a1a1a;
    float: left;
    margin-right: 12px;
    line-height: 1;
}
.insight-title { font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; color: #ff0000; margin-bottom: 4px; }
.insight-body { font-size: 0.95rem; color: #aaa; line-height: 1.6; }
.insight-highlight { color: #fff; font-weight: 600; }

/* ── Divider ── */
.yt-divider {
    border: none;
    border-top: 1px solid #1a1a1a;
    margin: 2.5rem 0;
}

/* ── Metric pill ── */
.pill {
    display: inline-block;
    background: #1a0000;
    border: 1px solid #3a0000;
    color: #ff6666;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 10px;
    border-radius: 999px;
    margin: 2px;
}

/* ── Table styling ── */
.stDataFrame { background: #111 !important; border-radius: 8px !important; }
.stDataFrame th { background: #1a1a1a !important; color: #ff0000 !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.7rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; }
.stDataFrame td { color: #ccc !important; font-size: 0.85rem !important; }

/* ── Plotly chart container ── */
.stPlotlyChart { background: transparent !important; }

/* ── Metric override ── */
[data-testid="stMetricValue"] { font-family: 'Bebas Neue', sans-serif !important; font-size: 1.8rem !important; color: #fff !important; }
[data-testid="stMetricLabel"] { color: #666 !important; font-size: 0.7rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; }

/* ── Header strip ── */
.top-strip {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.8rem 0;
    border-bottom: 1px solid #1a1a1a;
    margin-bottom: 1.5rem;
}
.top-logo { font-family: 'Bebas Neue', sans-serif; font-size: 1.4rem; letter-spacing: 4px; color: #ff0000; }
.top-tag { font-size: 0.65rem; letter-spacing: 2px; color: #444; text-transform: uppercase; }
</style>
""", unsafe_allow_html=True)

# ─── PLOT DEFAULTS ────────────────────────────────────────────────────────────
PLOT_BG   = "#0a0a0a"
PAPER_BG  = "#0a0a0a"
GRID_CLR  = "#1a1a1a"
FONT_CLR  = "#888"
RED       = "#ff0000"
RED2      = "#cc0000"
RED_PALE  = "#ff6666"
RED_SCALE = [[0.0,"#1a0000"],[0.35,"#6b0000"],[0.65,"#cc0000"],[1.0,"#ff3333"]]

def style_fig(fig, title="", height=360):
    fig.update_layout(
        title=dict(text=title, font=dict(family="Bebas Neue", size=18, color="#fff"), x=0),
        paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG,
        font=dict(family="DM Sans", color=FONT_CLR, size=12),
        height=height,
        margin=dict(l=16, r=16, t=44, b=16),
        legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#333"),
        xaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, tickfont=dict(size=10)),
        yaxis=dict(gridcolor=GRID_CLR, zerolinecolor=GRID_CLR, tickfont=dict(size=10)),
    )
    return fig

# ─── HELPERS ─────────────────────────────────────────────────────────────────
def fmt(n):
    if n >= 1_000_000_000: return f"{n/1_000_000_000:.2f}B"
    if n >= 1_000_000:     return f"{n/1_000_000:.2f}M"
    if n >= 1_000:         return f"{n/1_000:.1f}K"
    return str(n)

def parse_duration(d):
    try:    return isodate.parse_duration(d).total_seconds() / 60
    except: return 0

category_map = {
    "1":"Film","2":"Autos","10":"Music","17":"Sports","20":"Gaming","23":"Comedy",
    "24":"Entertainment","25":"News","26":"Howto","27":"Education","28":"Science"
}

day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]

# ─── API ──────────────────────────────────────────────────────────────────────
def get_yt(): return build("youtube", "v3", developerKey=API_KEY)

@st.cache_data(ttl=1800)
def fetch_channel(cid):
    r = get_yt().channels().list(part="snippet,statistics,contentDetails,brandingSettings", id=cid).execute()
    return r["items"][0] if r["items"] else None

@st.cache_data(ttl=1800)
def fetch_video_ids(pid, max_r=500):
    yt, ids, tok = get_yt(), [], None
    while len(ids) < max_r:
        r = yt.playlistItems().list(part="contentDetails", playlistId=pid,
            maxResults=min(50, max_r-len(ids)), pageToken=tok).execute()
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        tok = r.get("nextPageToken")
        if not tok: break
    return ids

@st.cache_data(ttl=1800)
def fetch_video_details(vids):
    if not vids: return pd.DataFrame()
    yt, rows = get_yt(), []
    for s in range(0, len(vids), 50):
        r = yt.videos().list(part="snippet,statistics,contentDetails",
                             id=",".join(vids[s:s+50])).execute()
        for it in r["items"]:
            st_ = it.get("statistics", {})
            sn  = it.get("snippet", {})
            cd  = it.get("contentDetails", {})
            rows.append({
                "Video ID":   it["id"],
                "Title":      sn.get("title",""),
                "PublishedAt":sn.get("publishedAt",""),
                "Views":      int(st_.get("viewCount",0)),
                "Likes":      int(st_.get("likeCount",0)),
                "Comments":   int(st_.get("commentCount",0)),
                "Tags":       sn.get("tags",[]),
                "CategoryId": sn.get("categoryId",""),
                "Duration":   cd.get("duration",""),
                "Definition": cd.get("definition",""),
                "Description":sn.get("description",""),
            })
    return pd.DataFrame(rows)

@st.cache_data(ttl=1800)
def fetch_playlists(cid):
    yt, pl, tok = get_yt(), [], None
    while True:
        r = yt.playlists().list(part="snippet,contentDetails", channelId=cid, maxResults=50, pageToken=tok).execute()
        pl += r["items"]; tok = r.get("nextPageToken")
        if not tok: break
    return pl

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-family:Bebas Neue;font-size:1.6rem;letter-spacing:4px;color:#ff0000;margin-bottom:4px">▶ YT DEEPDIVE</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.65rem;letter-spacing:2px;color:#444;text-transform:uppercase;margin-bottom:1.5rem">Channel Intelligence Platform</div>', unsafe_allow_html=True)
    
    channel_id = st.text_input("Channel ID", placeholder="UCxxxxxxxxxxxxxxxxxxxxxx", help="Find it in channel URL or About page")
    st.markdown("---")
    st.markdown('<div style="font-size:0.65rem;letter-spacing:2px;color:#444;text-transform:uppercase;margin-bottom:8px">Fetch Depth</div>', unsafe_allow_html=True)
    max_vids = st.slider("Max Videos to Fetch", 50, 500, 200, 50)
    st.markdown("---")
    st.markdown('<div style="font-size:0.65rem;color:#333;margin-top:2rem">Data refreshes every 30 min</div>', unsafe_allow_html=True)

# ─── HEADER STRIP ────────────────────────────────────────────────────────────
st.markdown('<div class="top-strip"><span class="top-logo">▶ YT DEEPDIVE</span><span class="top-tag">Channel Intelligence · 20 Advanced Insights</span></div>', unsafe_allow_html=True)

# ─── LANDING ─────────────────────────────────────────────────────────────────
if not channel_id:
    st.markdown("""
    <div style="text-align:center;padding:5rem 2rem">
        <div style="font-family:'Bebas Neue',sans-serif;font-size:5rem;color:#ff0000;letter-spacing:6px;line-height:1">CHANNEL<br>INTELLIGENCE</div>
        <div style="color:#444;font-size:0.9rem;letter-spacing:3px;text-transform:uppercase;margin:1rem 0 2rem">20 Advanced Insights · Deep Analytics · YouTube Data API</div>
        <div style="color:#333;font-size:0.85rem">Enter a Channel ID in the sidebar to begin</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ─── DATA LOAD ────────────────────────────────────────────────────────────────
with st.spinner("Fetching channel data…"):
    channel = fetch_channel(channel_id)
    if not channel:
        st.error("Channel not found. Verify the Channel ID.")
        st.stop()

    uploads_pid = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    
    with st.spinner("Loading videos…"):
        vids = fetch_video_ids(uploads_pid, max_r=max_vids)
        df = fetch_video_details(vids)
        playlists = fetch_playlists(channel_id)

# ─── PREPROCESSING ────────────────────────────────────────────────────────────
df["DurationMin"]   = df["Duration"].map(parse_duration)
df["PublishedDate"] = pd.to_datetime(df["PublishedAt"], errors="coerce", utc=True)
df["Month"]         = df["PublishedDate"].dt.to_period("M").astype(str)
df["DayOfWeek"]     = df["PublishedDate"].dt.day_name()
df["Year"]          = df["PublishedDate"].dt.year
df["Hour"]          = df["PublishedDate"].dt.hour
df["WeekNum"]       = df["PublishedDate"].dt.isocalendar().week.astype(int)
df["Quarter"]       = df["PublishedDate"].dt.quarter
df["Category"]      = df["CategoryId"].map(lambda x: category_map.get(x, "Other"))
df["TagCount"]      = df["Tags"].map(len)
df["EngRate"]       = np.where(df["Views"]>0, (df["Likes"]+df["Comments"])/df["Views"]*100, 0)
df["LikeRate"]      = np.where(df["Views"]>0, df["Likes"]/df["Views"]*100, 0)
df["CommentRate"]   = np.where(df["Views"]>0, df["Comments"]/df["Views"]*100, 0)
df["IsHD"]          = df["Definition"].map(lambda x: "HD" if x=="hd" else "SD")
df["TitleLen"]      = df["Title"].map(len)
df["TitleWordCount"]= df["Title"].map(lambda t: len(t.split()))
df["HasEmoji"]      = df["Title"].map(lambda t: bool(re.search(r'[^\x00-\x7F]', t)))
df["HasNumbers"]    = df["Title"].map(lambda t: bool(re.search(r'\d', t)))
df["DescLen"]       = df["Description"].map(len)
df["Engagement"]    = df["Likes"] + df["Comments"]

ch_stats  = channel["statistics"]
ch_snip   = channel["snippet"]
total_subs  = int(ch_stats.get("subscriberCount", 0))
total_views = int(ch_stats.get("viewCount", 0))
total_vids  = int(ch_stats.get("videoCount", 0))

# ─── HERO BANNER ─────────────────────────────────────────────────────────────
thumb = ch_snip["thumbnails"].get("high", ch_snip["thumbnails"].get("default", {})).get("url","")
col_img, col_info = st.columns([1, 5])
with col_img:
    if thumb: st.image(thumb, width=90)
with col_info:
    st.markdown(f"""
    <div class="hero-banner">
        <div class="hero-channel-name">{ch_snip['title']}</div>
        <div class="hero-handle">▶ {fmt(total_subs)} subscribers · {fmt(total_views)} total views · {total_vids:,} videos</div>
    </div>
    """, unsafe_allow_html=True)

# ─── TOP KPIs ─────────────────────────────────────────────────────────────────
avg_views_per_vid  = df["Views"].mean()  if not df.empty else 0
avg_eng_rate       = df["EngRate"].mean() if not df.empty else 0
top_vid_views      = df["Views"].max()   if not df.empty else 0
uploads_last_30    = df[df["PublishedDate"] >= (pd.Timestamp.now(tz="UTC") - pd.Timedelta(days=30))].shape[0]

kpis = [
    ("Subscribers",      fmt(total_subs),    "▶ Total"),
    ("Channel Views",    fmt(total_views),   "▶ Lifetime"),
    ("Avg Views/Video",  fmt(int(avg_views_per_vid)), "▶ Analyzed"),
    ("Avg Engagement",   f"{avg_eng_rate:.2f}%", "▶ Rate"),
    ("Peak Video",       fmt(top_vid_views), "▶ Max Views"),
    ("Uploads (30d)",    str(uploads_last_30),"▶ Recent"),
]

cols = st.columns(6)
for i,(label, val, delta) in enumerate(kpis):
    with cols[i]:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{val}</div>
            <div class="kpi-delta">{delta}</div>
        </div>""", unsafe_allow_html=True)

st.markdown('<hr class="yt-divider">', unsafe_allow_html=True)

if df.empty:
    st.warning("No videos found.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 1 — CHANNEL GROWTH MOMENTUM
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">01 — Growth Momentum</div><div class="section-sub">Cumulative velocity of views & subscribers over the channel\'s lifetime</div>', unsafe_allow_html=True)

growth = df.sort_values("PublishedDate").copy()
growth["CumViews"]      = growth["Views"].cumsum()
growth["CumEngagement"] = growth["Engagement"].cumsum()
growth["CumLikes"]      = growth["Likes"].cumsum()
growth["VideoNum"]      = range(1, len(growth)+1)

fig = make_subplots(rows=1, cols=2, subplot_titles=("Cumulative Views Growth", "Cumulative Engagement Growth"))
fig.add_trace(go.Scatter(x=growth["PublishedDate"], y=growth["CumViews"], fill="tozeroy",
    line=dict(color=RED, width=2), fillcolor="rgba(255,0,0,0.07)", name="Cum. Views"), row=1, col=1)
fig.add_trace(go.Scatter(x=growth["PublishedDate"], y=growth["CumEngagement"], fill="tozeroy",
    line=dict(color=RED_PALE, width=2), fillcolor="rgba(255,100,100,0.07)", name="Cum. Engagement"), row=1, col=2)
fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, font=dict(color=FONT_CLR), height=340,
    margin=dict(l=16,r=16,t=44,b=16), showlegend=True, legend=dict(bgcolor="rgba(0,0,0,0)"))
fig.update_xaxes(gridcolor=GRID_CLR); fig.update_yaxes(gridcolor=GRID_CLR)
fig.update_annotations(font=dict(family="Bebas Neue", size=14, color="#aaa"))
st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 2 — UPLOAD FREQUENCY HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">02 — Upload Frequency Heatmap</div><div class="section-sub">When does this channel publish? Day × Hour density map</div>', unsafe_allow_html=True)

heat = df.groupby(["DayOfWeek","Hour"]).size().reset_index(name="Count")
heat_pivot = heat.pivot(index="DayOfWeek", columns="Hour", values="Count").reindex(day_order).fillna(0)

fig = go.Figure(go.Heatmap(z=heat_pivot.values, x=list(range(24)), y=day_order,
    colorscale=RED_SCALE, showscale=True, hoverongaps=False,
    hovertemplate="Day: %{y}<br>Hour: %{x}:00<br>Uploads: %{z}<extra></extra>"))
style_fig(fig, "Upload Heatmap — Day × Hour (UTC)", 320)
fig.update_xaxes(ticktext=[f"{h:02d}:00" for h in range(0,24,3)], tickvals=list(range(0,24,3)))
st.plotly_chart(fig, use_container_width=True)

best_day = df["DayOfWeek"].value_counts().idxmax()
best_hr  = df["Hour"].value_counts().idxmax()
st.markdown(f'<div class="insight-card"><div class="insight-num">02</div><div class="insight-title">Best Upload Window</div><div class="insight-body">This channel uploads most on <span class="insight-highlight">{best_day}s at {best_hr:02d}:00 UTC</span>. Scheduling content around this window suggests it\'s when the audience is most receptive or the creator is most active.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 3 — VIDEO PERFORMANCE QUADRANT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">03 — Performance Quadrant</div><div class="section-sub">Views vs Engagement Rate — spot viral hits, hidden gems & underperformers</div>', unsafe_allow_html=True)

med_views = df["Views"].median()
med_eng   = df["EngRate"].median()
df["Quadrant"] = df.apply(lambda r:
    "🔴 Viral Hit"       if r["Views"]>=med_views and r["EngRate"]>=med_eng else
    "🟠 Hidden Gem"      if r["Views"]<med_views  and r["EngRate"]>=med_eng else
    "🟡 Broad Reach"     if r["Views"]>=med_views and r["EngRate"]<med_eng  else
    "⚫ Underperformer", axis=1)

color_map = {"🔴 Viral Hit":"#ff2222","🟠 Hidden Gem":"#ff8800","🟡 Broad Reach":"#ffcc00","⚫ Underperformer":"#444"}
fig = px.scatter(df, x="Views", y="EngRate", color="Quadrant", color_discrete_map=color_map,
    size="Likes", size_max=28, hover_name="Title",
    hover_data={"Views":True,"EngRate":":.2f","Likes":True,"Quadrant":False},
    labels={"EngRate":"Engagement Rate (%)","Views":"Total Views"})
fig.add_vline(x=med_views, line_dash="dot", line_color="#333")
fig.add_hline(y=med_eng,   line_dash="dot", line_color="#333")
style_fig(fig, "Video Performance Quadrant", 440)
st.plotly_chart(fig, use_container_width=True)

viral = df[df["Quadrant"]=="🔴 Viral Hit"].shape[0]
gems  = df[df["Quadrant"]=="🟠 Hidden Gem"].shape[0]
st.markdown(f'<div class="insight-card"><div class="insight-num">03</div><div class="insight-title">Quadrant Breakdown</div><div class="insight-body">Out of {len(df)} videos: <span class="insight-highlight">{viral} Viral Hits</span> (high views + high engagement), <span class="insight-highlight">{gems} Hidden Gems</span> (lower views but deeply engaging). Hidden gems are potential candidates for promotion or series expansion.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 4 — TITLE ANATOMY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">04 — Title Anatomy & Impact</div><div class="section-sub">How title length, emojis, numbers and word count correlate with views</div>', unsafe_allow_html=True)

c1, c2 = st.columns(2)
with c1:
    fig = px.scatter(df, x="TitleLen", y="Views", color="EngRate",
        color_continuous_scale=RED_SCALE, hover_name="Title", size_max=12,
        labels={"TitleLen":"Title Length (chars)","Views":"Views","EngRate":"Eng%"})
    style_fig(fig, "Title Length vs Views", 320)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    grp = df.groupby("HasEmoji")["Views"].median().reset_index()
    grp["Label"] = grp["HasEmoji"].map({True:"With Emoji 🔥", False:"No Emoji"})
    fig = px.bar(grp, x="Label", y="Views", color="Views", color_continuous_scale=RED_SCALE,
                 labels={"Views":"Median Views"})
    style_fig(fig, "Emoji in Title → Median Views", 320)
    st.plotly_chart(fig, use_container_width=True)

optimal_len = df.groupby(pd.cut(df["TitleLen"], bins=5))["Views"].median().idxmax()
st.markdown(f'<div class="insight-card"><div class="insight-num">04</div><div class="insight-title">Title Strategy Signal</div><div class="insight-body">Optimal title length range: <span class="insight-highlight">{optimal_len}</span> characters yielding highest median views. Titles with emojis get <span class="insight-highlight">{"more" if df[df["HasEmoji"]]["Views"].median() > df[~df["HasEmoji"]]["Views"].median() else "fewer"} views</span> on this channel. Numbers in titles: used in {df["HasNumbers"].mean()*100:.0f}% of videos.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 5 — VIDEO DURATION SWEET SPOT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">05 — Duration Sweet Spot</div><div class="section-sub">Which video lengths drive the most views and engagement on this channel</div>', unsafe_allow_html=True)

df_dur = df[df["DurationMin"] < df["DurationMin"].quantile(0.98)].copy()
bins   = [0,2,5,10,15,20,30,45,60,120,1000]
labels = ["<2m","2–5m","5–10m","10–15m","15–20m","20–30m","30–45m","45–60m","1–2h",">2h"]
df_dur["DurBin"] = pd.cut(df_dur["DurationMin"], bins=bins, labels=labels)
dur_agg = df_dur.groupby("DurBin").agg(
    MedViews=("Views","median"), MedEng=("EngRate","median"), Count=("Video ID","count")).reset_index()
dur_agg = dur_agg[dur_agg["Count"]>=1]

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=dur_agg["DurBin"].astype(str), y=dur_agg["MedViews"], name="Median Views",
    marker_color=RED, opacity=0.9), secondary_y=False)
fig.add_trace(go.Scatter(x=dur_agg["DurBin"].astype(str), y=dur_agg["MedEng"], name="Median Eng%",
    line=dict(color=RED_PALE, width=2), mode="lines+markers"), secondary_y=True)
fig.add_trace(go.Scatter(x=dur_agg["DurBin"].astype(str), y=dur_agg["Count"], name="# Videos",
    line=dict(color="#444", width=1, dash="dot"), mode="lines+markers"), secondary_y=True)
fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, height=360,
    font=dict(color=FONT_CLR), margin=dict(l=16,r=16,t=44,b=16),
    title=dict(text="Duration Bucket Analysis", font=dict(family="Bebas Neue",size=18,color="#fff"), x=0),
    legend=dict(bgcolor="rgba(0,0,0,0)"))
fig.update_xaxes(gridcolor=GRID_CLR); fig.update_yaxes(gridcolor=GRID_CLR)
st.plotly_chart(fig, use_container_width=True)

best_dur_bin = dur_agg.loc[dur_agg["MedViews"].idxmax(), "DurBin"]
st.markdown(f'<div class="insight-card"><div class="insight-num">05</div><div class="insight-title">Duration Sweet Spot</div><div class="insight-body">Videos in the <span class="insight-highlight">{best_dur_bin}</span> range achieve the highest median views on this channel. This is the creator\'s algorithmic comfort zone — the length their audience prefers.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 6 — MONTHLY PERFORMANCE TRENDS
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">06 — Monthly Performance Pulse</div><div class="section-sub">Views, Likes, Comments and Upload count per month</div>', unsafe_allow_html=True)

monthly = df.groupby("Month").agg(
    TotalViews=("Views","sum"), TotalLikes=("Likes","sum"),
    TotalComments=("Comments","sum"), Uploads=("Video ID","count"),
    AvgEngRate=("EngRate","mean")).reset_index().sort_values("Month")

fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
    subplot_titles=("Monthly Views & Engagement Rate", "Monthly Uploads & Comments"))
fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["TotalViews"], name="Total Views",
    marker_color=RED, opacity=0.8), row=1, col=1)
fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["AvgEngRate"], name="Avg Eng%",
    line=dict(color=RED_PALE, width=2), yaxis="y2"), row=1, col=1)
fig.add_trace(go.Bar(x=monthly["Month"], y=monthly["Uploads"], name="Uploads",
    marker_color="#333"), row=2, col=1)
fig.add_trace(go.Scatter(x=monthly["Month"], y=monthly["TotalComments"], name="Comments",
    line=dict(color=RED_PALE, width=1.5)), row=2, col=1)
fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, height=460,
    font=dict(color=FONT_CLR), margin=dict(l=16,r=16,t=44,b=16),
    legend=dict(bgcolor="rgba(0,0,0,0)"))
fig.update_xaxes(gridcolor=GRID_CLR); fig.update_yaxes(gridcolor=GRID_CLR)
fig.update_annotations(font=dict(family="Bebas Neue",size=13,color="#aaa"))
st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 7 — TOP TAGS INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">07 — Tag Intelligence</div><div class="section-sub">Which tags appear most, and which tags actually drive views</div>', unsafe_allow_html=True)

all_tags = [t.lower() for tags in df["Tags"] for t in tags if len(t)>2]
tag_freq = Counter(all_tags).most_common(30)

if tag_freq:
    tag_df = pd.DataFrame(tag_freq, columns=["Tag","Frequency"])
    tag_views = {}
    for _, row in df.iterrows():
        for t in row["Tags"]:
            t = t.lower()
            tag_views.setdefault(t, []).append(row["Views"])
    tag_df["AvgViews"] = tag_df["Tag"].map(lambda t: int(np.mean(tag_views.get(t,[0]))))
    
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(tag_df.head(15), x="Frequency", y="Tag", orientation="h",
            color="Frequency", color_continuous_scale=RED_SCALE)
        style_fig(fig, "Most Used Tags (Frequency)", 380)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        top_by_views = tag_df.sort_values("AvgViews", ascending=False).head(15)
        fig = px.bar(top_by_views, x="AvgViews", y="Tag", orientation="h",
            color="AvgViews", color_continuous_scale=RED_SCALE)
        style_fig(fig, "Tags by Avg Views (Effectiveness)", 380)
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    best_tag = tag_df.sort_values("AvgViews", ascending=False).iloc[0]
    most_used = tag_df.iloc[0]
    st.markdown(f'<div class="insight-card"><div class="insight-num">07</div><div class="insight-title">Tag Strategy</div><div class="insight-body">Most used tag: <span class="insight-highlight">#{most_used["Tag"]}</span> ({most_used["Frequency"]} videos). Highest-performing tag: <span class="insight-highlight">#{best_tag["Tag"]}</span> averaging <span class="insight-highlight">{fmt(best_tag["AvgViews"])} views</span>. This channel uses an avg of {df["TagCount"].mean():.1f} tags per video.</div></div>', unsafe_allow_html=True)
else:
    st.info("No tag data available for this channel.")

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 8 — VIEWS PER SUBSCRIBER EFFICIENCY
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">08 — Subscriber Leverage</div><div class="section-sub">What percentage of subscribers does each video typically reach?</div>', unsafe_allow_html=True)

if total_subs > 0:
    df["SubReachPct"] = df["Views"] / total_subs * 100
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(df, x="SubReachPct", nbins=20, color_discrete_sequence=[RED],
            labels={"SubReachPct":"% of Subscribers Reached"})
        style_fig(fig, "Distribution: % Subscriber Reach Per Video", 320)
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        reach_over_time = df.sort_values("PublishedDate").groupby("Month")["SubReachPct"].mean().reset_index()
        fig = px.line(reach_over_time, x="Month", y="SubReachPct", markers=True,
            color_discrete_sequence=[RED], labels={"SubReachPct":"Avg Sub Reach %"})
        style_fig(fig, "Avg Subscriber Reach % Over Time", 320)
        st.plotly_chart(fig, use_container_width=True)

    avg_reach = df["SubReachPct"].mean()
    st.markdown(f'<div class="insight-card"><div class="insight-num">08</div><div class="insight-title">Subscriber Leverage Score</div><div class="insight-body">On average, each video reaches <span class="insight-highlight">{avg_reach:.1f}%</span> of the subscriber base. Top video reached <span class="insight-highlight">{df["SubReachPct"].max():.1f}%</span>. Channels above 20% average have strong subscriber retention and notification click-through.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 9 — CONTENT VELOCITY & CADENCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">09 — Content Velocity & Cadence</div><div class="section-sub">Upload consistency, gaps between videos, and publishing rhythm</div>', unsafe_allow_html=True)

sorted_df = df.sort_values("PublishedDate").copy()
sorted_df["DaysSinceLast"] = sorted_df["PublishedDate"].diff().dt.total_seconds() / 86400
gaps = sorted_df["DaysSinceLast"].dropna()

c1, c2, c3 = st.columns(3)
with c1:
    fig = px.histogram(gaps, nbins=30, color_discrete_sequence=[RED],
        labels={"value":"Days Between Uploads","count":"Frequency"})
    style_fig(fig, "Gap Distribution (Days)", 280)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    dow_count = df["DayOfWeek"].value_counts().reindex(day_order).fillna(0).reset_index()
    dow_count.columns = ["Day","Count"]
    fig = px.bar(dow_count, x="Day", y="Count", color="Count", color_continuous_scale=RED_SCALE)
    style_fig(fig, "Uploads by Day of Week", 280)
    st.plotly_chart(fig, use_container_width=True)
with c3:
    yearly = df.groupby("Year").size().reset_index(name="Uploads")
    fig = px.bar(yearly, x="Year", y="Uploads", color="Uploads", color_continuous_scale=RED_SCALE)
    style_fig(fig, "Annual Upload Volume", 280)
    st.plotly_chart(fig, use_container_width=True)

avg_gap = gaps.mean()
st.markdown(f'<div class="insight-card"><div class="insight-num">09</div><div class="insight-title">Upload Cadence</div><div class="insight-body">Average gap between uploads: <span class="insight-highlight">{avg_gap:.1f} days</span> (~{7/avg_gap:.1f}x per week). Most consistent upload day: <span class="insight-highlight">{df["DayOfWeek"].value_counts().idxmax()}</span>. Longest gap: <span class="insight-highlight">{gaps.max():.0f} days</span>.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 10 — COMMENT-TO-LIKE RATIO (CONTROVERSY SCORE)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">10 — Controversy Score</div><div class="section-sub">Comment-to-Like ratio reveals which videos spark debate vs pure appreciation</div>', unsafe_allow_html=True)

df_c = df[df["Likes"]>10].copy()
df_c["ControversyScore"] = df_c["Comments"] / (df_c["Likes"] + 1) * 100

top_controversial = df_c.nlargest(10, "ControversyScore")[["Title","Views","Likes","Comments","ControversyScore"]]
top_beloved       = df_c.nsmallest(10, "ControversyScore")[["Title","Views","Likes","Comments","ControversyScore"]]

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(top_controversial.sort_values("ControversyScore"), x="ControversyScore", y="Title",
        orientation="h", color="ControversyScore", color_continuous_scale=RED_SCALE,
        labels={"ControversyScore":"Score"})
    style_fig(fig, "Most Controversial Videos", 340)
    fig.update_yaxes(autorange="reversed", tickfont=dict(size=9))
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.scatter(df_c, x="Likes", y="Comments", color="ControversyScore",
        color_continuous_scale=RED_SCALE, hover_name="Title", size="Views", size_max=24,
        labels={"ControversyScore":"Controversy"})
    style_fig(fig, "Likes vs Comments Space", 340)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 11 — VIRAL ACCELERATION INDEX
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">11 — Viral Acceleration Index</div><div class="section-sub">Views per day since publish — which old videos are still gaining traction</div>', unsafe_allow_html=True)

now = pd.Timestamp.now(tz="UTC")
df["AgeDays"]       = (now - df["PublishedDate"]).dt.total_seconds() / 86400
df["ViewsPerDay"]   = df.apply(lambda r: r["Views"]/r["AgeDays"] if r["AgeDays"]>0 else 0, axis=1)
df["ViralIndex"]    = df["ViewsPerDay"] * df["EngRate"]

top_viral = df.nlargest(15, "ViralIndex")[["Title","Views","ViewsPerDay","EngRate","ViralIndex","AgeDays"]]

fig = px.scatter(df, x="AgeDays", y="ViewsPerDay", color="ViralIndex", size="Engagement",
    size_max=30, color_continuous_scale=RED_SCALE, hover_name="Title",
    labels={"AgeDays":"Age (days)","ViewsPerDay":"Views/Day","ViralIndex":"Viral Index"})
style_fig(fig, "Viral Acceleration — Age vs Views Per Day (size = engagement)", 420)
st.plotly_chart(fig, use_container_width=True)

best_viral = df.nlargest(1, "ViralIndex").iloc[0]
st.markdown(f'<div class="insight-card"><div class="insight-num">11</div><div class="insight-title">Highest Viral Index</div><div class="insight-body"><span class="insight-highlight">{best_viral["Title"][:60]}…</span> is the most algorithmically alive video with <span class="insight-highlight">{fmt(int(best_viral["ViewsPerDay"]))} views/day</span> and a Viral Index of <span class="insight-highlight">{best_viral["ViralIndex"]:.1f}</span>.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 12 — CONTENT MIX RADAR
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">12 — Content DNA Radar</div><div class="section-sub">How the channel\'s content mix breaks down across YouTube categories</div>', unsafe_allow_html=True)

cat_agg = df.groupby("Category").agg(
    Count=("Video ID","count"), TotalViews=("Views","sum"),
    AvgEng=("EngRate","mean"), TotalLikes=("Likes","sum")).reset_index()

c1, c2 = st.columns(2)
with c1:
    fig = px.pie(cat_agg, names="Category", values="Count",
        color_discrete_sequence=px.colors.sequential.Reds[::-1][:len(cat_agg)])
    fig.update_traces(textposition="inside", textinfo="percent+label",
        marker=dict(line=dict(color="#0a0a0a", width=2)))
    style_fig(fig, "Upload Count by Category", 340)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    if len(cat_agg) >= 3:
        cats = cat_agg["Category"].tolist()
        vals_views = (cat_agg["TotalViews"] / cat_agg["TotalViews"].max()).tolist()
        vals_eng   = (cat_agg["AvgEng"]    / cat_agg["AvgEng"].max()).tolist()
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=vals_views+[vals_views[0]], theta=cats+[cats[0]],
            fill="toself", name="Relative Views",
            line_color=RED, fillcolor="rgba(255,0,0,0.12)"))
        fig.add_trace(go.Scatterpolar(r=vals_eng+[vals_eng[0]], theta=cats+[cats[0]],
            fill="toself", name="Relative Engagement",
            line_color=RED_PALE, fillcolor="rgba(255,100,100,0.08)"))
        fig.update_layout(polar=dict(
            radialaxis=dict(visible=True, range=[0,1], gridcolor="#1a1a1a", tickfont=dict(color="#444")),
            angularaxis=dict(gridcolor="#1a1a1a"),
            bgcolor=PAPER_BG),
            paper_bgcolor=PAPER_BG, height=340, font=dict(color=FONT_CLR),
            margin=dict(l=40,r=40,t=60,b=40),
            title=dict(text="Content Category Radar", font=dict(family="Bebas Neue",size=18,color="#fff"), x=0),
            legend=dict(bgcolor="rgba(0,0,0,0)"))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need 3+ categories for radar.")

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 13 — TOP 10 VIDEOS DEEP DIVE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">13 — Top 10 Video Profiles</div><div class="section-sub">Multi-metric comparison of the channel\'s best-performing videos</div>', unsafe_allow_html=True)

top10 = df.nlargest(10, "Views")[["Title","Views","Likes","Comments","DurationMin","EngRate","TagCount"]].copy()
top10["Title_short"] = top10["Title"].map(lambda t: t[:35]+"…" if len(t)>35 else t)

fig = make_subplots(rows=1, cols=3, subplot_titles=("Views","Likes","Engagement Rate (%)"))
colors = [f"rgba(255,{max(0,int(30+i*20))},{max(0,int(30+i*20))},0.9)" for i in range(10)]
for col_idx, metric in enumerate(["Views","Likes","EngRate"], start=1):
    fig.add_trace(go.Bar(x=top10[metric], y=top10["Title_short"], orientation="h",
        marker_color=[RED]*10 if col_idx==1 else ["#cc0000"]*10 if col_idx==2 else ["#ff4444"]*10,
        showlegend=False, name=metric), row=1, col=col_idx)
fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, height=400,
    font=dict(color=FONT_CLR, size=10), margin=dict(l=16,r=16,t=44,b=16))
fig.update_xaxes(gridcolor=GRID_CLR); fig.update_yaxes(gridcolor=GRID_CLR, autorange="reversed")
fig.update_annotations(font=dict(family="Bebas Neue",size=13,color="#aaa"))
st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 14 — ENGAGEMENT DECAY CURVE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">14 — Engagement Decay Curve</div><div class="section-sub">Does engagement rate drop as videos age? Measuring freshness vs longevity</div>', unsafe_allow_html=True)

df_decay = df[(df["AgeDays"]>0) & (df["AgeDays"]<1500)].copy()
df_decay["AgeGroup"] = pd.cut(df_decay["AgeDays"], bins=[0,30,90,180,365,730,1500],
    labels=["0–30d","1–3m","3–6m","6m–1y","1–2y","2y+"])
decay_agg = df_decay.groupby("AgeGroup").agg(
    AvgEngRate=("EngRate","mean"), AvgViews=("Views","mean"), Count=("Video ID","count")).reset_index()

fig = make_subplots(specs=[[{"secondary_y": True}]])
fig.add_trace(go.Bar(x=decay_agg["AgeGroup"].astype(str), y=decay_agg["AvgViews"],
    name="Avg Views", marker_color=RED, opacity=0.8), secondary_y=False)
fig.add_trace(go.Scatter(x=decay_agg["AgeGroup"].astype(str), y=decay_agg["AvgEngRate"],
    name="Avg Eng%", line=dict(color=RED_PALE, width=2.5), mode="lines+markers+text",
    text=decay_agg["AvgEngRate"].map(lambda x: f"{x:.2f}%"), textposition="top center",
    textfont=dict(color=RED_PALE, size=10)), secondary_y=True)
fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, height=360,
    font=dict(color=FONT_CLR), margin=dict(l=16,r=16,t=44,b=16),
    title=dict(text="Engagement Decay by Video Age", font=dict(family="Bebas Neue",size=18,color="#fff"), x=0),
    legend=dict(bgcolor="rgba(0,0,0,0)"))
fig.update_xaxes(gridcolor=GRID_CLR); fig.update_yaxes(gridcolor=GRID_CLR)
st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 15 — PLAYLIST PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">15 — Playlist Architecture</div><div class="section-sub">How the channel organizes content and playlist size distribution</div>', unsafe_allow_html=True)

if playlists:
    pl_df = pd.DataFrame([{
        "Title":      p["snippet"]["title"],
        "VideoCount": p["contentDetails"].get("itemCount", 0),
        "Description":p["snippet"].get("description","")
    } for p in playlists])
    pl_df = pl_df.sort_values("VideoCount", ascending=False)

    c1, c2 = st.columns([3,2])
    with c1:
        fig = px.bar(pl_df.head(15), x="VideoCount", y="Title", orientation="h",
            color="VideoCount", color_continuous_scale=RED_SCALE,
            labels={"VideoCount":"Video Count"})
        style_fig(fig, f"Top {min(15,len(pl_df))} Playlists by Size", 380)
        fig.update_yaxes(autorange="reversed", tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.histogram(pl_df, x="VideoCount", nbins=10, color_discrete_sequence=[RED])
        style_fig(fig, "Playlist Size Distribution", 380)
        st.plotly_chart(fig, use_container_width=True)

    avg_pl_size = pl_df["VideoCount"].mean()
    st.markdown(f'<div class="insight-card"><div class="insight-num">15</div><div class="insight-title">Playlist Strategy</div><div class="insight-body">Channel has <span class="insight-highlight">{len(playlists)} playlists</span> with avg <span class="insight-highlight">{avg_pl_size:.0f} videos each</span>. Largest playlist: <span class="insight-highlight">{pl_df.iloc[0]["Title"]}</span> ({pl_df.iloc[0]["VideoCount"]} videos). More playlists = better watch-time chains for the algorithm.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 16 — HD vs SD QUALITY IMPACT
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">16 — Quality & Production Evolution</div><div class="section-sub">HD vs SD adoption over time and its correlation with viewership</div>', unsafe_allow_html=True)

quality_agg = df.groupby(["Month","IsHD"]).size().reset_index(name="Count").sort_values("Month")
quality_views = df.groupby("IsHD").agg(AvgViews=("Views","mean"), Count=("Video ID","count")).reset_index()

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(quality_agg, x="Month", y="Count", color="IsHD",
        color_discrete_map={"HD":RED,"SD":"#333"},
        labels={"Count":"Uploads","IsHD":"Quality"}, barmode="stack")
    style_fig(fig, "HD vs SD Uploads Over Time", 320)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.bar(quality_views, x="IsHD", y="AvgViews", color="AvgViews",
        color_continuous_scale=RED_SCALE, text=quality_views["AvgViews"].map(lambda x: fmt(int(x))),
        labels={"AvgViews":"Avg Views","IsHD":"Quality"})
    fig.update_traces(textposition="outside", textfont_color="#fff")
    style_fig(fig, "HD vs SD — Avg Views Comparison", 320)
    st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 17 — VIEWS CONCENTRATION (PARETO ANALYSIS)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">17 — Pareto: Views Concentration</div><div class="section-sub">What % of videos drive 80% of total views? Channel dependency risk analysis</div>', unsafe_allow_html=True)

pareto_df = df.sort_values("Views", ascending=False).copy()
pareto_df["CumViews"] = pareto_df["Views"].cumsum()
pareto_df["CumViewsPct"] = pareto_df["CumViews"] / pareto_df["Views"].sum() * 100
pareto_df["VideoRank"] = range(1, len(pareto_df)+1)
pareto_df["VideoRankPct"] = pareto_df["VideoRank"] / len(pareto_df) * 100

fig = go.Figure()
fig.add_trace(go.Scatter(x=pareto_df["VideoRankPct"], y=pareto_df["CumViewsPct"],
    fill="tozeroy", line=dict(color=RED, width=2.5),
    fillcolor="rgba(255,0,0,0.08)", name="Cumulative Views %",
    hovertemplate="Top %{x:.1f}% videos → %{y:.1f}% of views"))
fig.add_hline(y=80, line_dash="dot", line_color="#444",
    annotation_text="80% of views", annotation_font_color="#888")
fig.add_vline(x=20, line_dash="dot", line_color="#444",
    annotation_text="Top 20%", annotation_font_color="#888")
style_fig(fig, "Pareto Curve — Views Concentration", 380)
fig.update_xaxes(title="% of Videos (Ranked by Views)")
fig.update_yaxes(title="Cumulative % of Total Views")
st.plotly_chart(fig, use_container_width=True)

pct_vids_for_80 = pareto_df[pareto_df["CumViewsPct"]<=80].shape[0] / len(pareto_df) * 100
st.markdown(f'<div class="insight-card"><div class="insight-num">17</div><div class="insight-title">Views Concentration Risk</div><div class="insight-body">Only <span class="insight-highlight">{pct_vids_for_80:.1f}% of videos</span> account for 80% of total channel views. {"This is a high dependency — if those videos are demonetized or taken down, the channel loses most of its traffic." if pct_vids_for_80 < 15 else "A reasonably distributed viewership — the channel isn\'t overly dependent on a few viral hits."}</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 18 — DESCRIPTION LENGTH vs PERFORMANCE
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">18 — SEO Description Impact</div><div class="section-sub">Does investing in longer, richer descriptions lead to more views?</div>', unsafe_allow_html=True)

desc_bins = [0, 100, 300, 600, 1000, 2000, 10000]
desc_labels = ["<100","100–300","300–600","600–1k","1k–2k","2k+"]
df["DescBin"] = pd.cut(df["DescLen"], bins=desc_bins, labels=desc_labels)
desc_agg = df.groupby("DescBin").agg(
    MedViews=("Views","median"), MedEng=("EngRate","median"), Count=("Video ID","count")).reset_index()

c1, c2 = st.columns(2)
with c1:
    fig = px.bar(desc_agg, x="DescBin", y="MedViews", color="MedViews",
        color_continuous_scale=RED_SCALE, text=desc_agg["MedViews"].map(lambda x: fmt(int(x))),
        labels={"DescBin":"Description Length","MedViews":"Median Views"})
    fig.update_traces(textposition="outside", textfont_color="#fff")
    style_fig(fig, "Description Length → Median Views", 320)
    st.plotly_chart(fig, use_container_width=True)
with c2:
    fig = px.scatter(df, x="DescLen", y="Views", color="EngRate",
        color_continuous_scale=RED_SCALE, hover_name="Title", opacity=0.7,
        labels={"DescLen":"Description Length","Views":"Views","EngRate":"Eng%"})
    style_fig(fig, "Description Length vs Views (scatter)", 320)
    st.plotly_chart(fig, use_container_width=True)

best_desc_bin = desc_agg.loc[desc_agg["MedViews"].idxmax(), "DescBin"]
st.markdown(f'<div class="insight-card"><div class="insight-num">18</div><div class="insight-title">SEO Insight</div><div class="insight-body">Videos with <span class="insight-highlight">{best_desc_bin} character descriptions</span> achieve the highest median views. Avg description length on this channel: <span class="insight-highlight">{df["DescLen"].mean():.0f} chars</span>.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 19 — YEARLY PERFORMANCE BENCHMARK
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">19 — Year-over-Year Benchmark</div><div class="section-sub">How the channel grew (or declined) across each calendar year</div>', unsafe_allow_html=True)

yr_agg = df.groupby("Year").agg(
    Uploads=("Video ID","count"), TotalViews=("Views","sum"),
    AvgViews=("Views","mean"), AvgEng=("EngRate","mean"),
    TotalLikes=("Likes","sum")).reset_index()
yr_agg = yr_agg[yr_agg["Year"] >= 2010]

if len(yr_agg) >= 2:
    yr_agg["ViewsGrowth"] = yr_agg["TotalViews"].pct_change() * 100
    yr_agg["UploadsGrowth"] = yr_agg["Uploads"].pct_change() * 100

    fig = make_subplots(rows=2, cols=2,
        subplot_titles=("Annual Total Views","Annual Avg Views/Video","Uploads Per Year","Avg Engagement Rate"))
    metrics = [("TotalViews",1,1),("AvgViews",1,2),("Uploads",2,1),("AvgEng",2,2)]
    for metric, row, col in metrics:
        fig.add_trace(go.Bar(x=yr_agg["Year"], y=yr_agg[metric], name=metric,
            marker_color=RED, showlegend=False), row=row, col=col)
    fig.update_layout(paper_bgcolor=PAPER_BG, plot_bgcolor=PLOT_BG, height=500,
        font=dict(color=FONT_CLR), margin=dict(l=16,r=16,t=44,b=16))
    fig.update_xaxes(gridcolor=GRID_CLR); fig.update_yaxes(gridcolor=GRID_CLR)
    fig.update_annotations(font=dict(family="Bebas Neue",size=13,color="#aaa"))
    st.plotly_chart(fig, use_container_width=True)

    best_year = yr_agg.loc[yr_agg["TotalViews"].idxmax(), "Year"]
    st.markdown(f'<div class="insight-card"><div class="insight-num">19</div><div class="insight-title">Peak Performance Year</div><div class="insight-body"><span class="insight-highlight">{int(best_year)}</span> was the channel\'s strongest year by total views, with <span class="insight-highlight">{fmt(int(yr_agg.loc[yr_agg["Year"]==best_year,"TotalViews"].values[0]))}</span> views across {int(yr_agg.loc[yr_agg["Year"]==best_year,"Uploads"].values[0])} uploads.</div></div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# INSIGHT 20 — CHANNEL SCORE CARD
# ══════════════════════════════════════════════════════════════════════════════
st.markdown('<div class="section-title">20 — Channel Score Card</div><div class="section-sub">A composite intelligence summary — your channel\'s strengths, blind spots & opportunities</div>', unsafe_allow_html=True)

# Compute scores (0–100)
def score_percentile(val, series): return min(100, int(np.percentile(series, (series <= val).mean()*100) if len(series)>0 else 50))

avg_eng_score    = min(100, int(avg_eng_rate * 10))
consistency_score= min(100, max(0, int(100 - gaps.std() / (gaps.mean()+0.01) * 30))) if len(gaps)>1 else 50
reach_score      = min(100, int(avg_reach * 3)) if total_subs>0 else 50
content_div_score= min(100, int(df["Category"].nunique() / 10 * 100))
seo_score        = min(100, int(df["TagCount"].mean() / 30 * 100 + df["DescLen"].mean() / 3000 * 50))
momentum_score   = min(100, int(df[df["AgeDays"]<90]["ViewsPerDay"].mean() / (df["ViewsPerDay"].mean()+0.01) * 50)) if len(df[df["AgeDays"]<90])>0 else 50

scores = {
    "Engagement":    avg_eng_score,
    "Consistency":   consistency_score,
    "Reach":         reach_score,
    "Content Diversity": content_div_score,
    "SEO Depth":     seo_score,
    "Momentum":      momentum_score,
}

score_cats = list(scores.keys())
score_vals  = list(scores.values())
overall = int(np.mean(score_vals))

c1, c2 = st.columns([2,3])
with c1:
    for cat, val in scores.items():
        color = "#ff0000" if val>=70 else "#cc5500" if val>=40 else "#443333"
        st.markdown(f"""
        <div style="margin-bottom:10px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                <span style="font-size:0.75rem;letter-spacing:1px;text-transform:uppercase;color:#888">{cat}</span>
                <span style="font-family:'JetBrains Mono';font-size:0.75rem;color:#fff">{val}</span>
            </div>
            <div style="background:#1a1a1a;border-radius:4px;height:6px;overflow:hidden">
                <div style="background:{color};width:{val}%;height:100%;border-radius:4px;transition:width 0.6s"></div>
            </div>
        </div>""", unsafe_allow_html=True)
with c2:
    fig = go.Figure(go.Scatterpolar(
        r=score_vals + [score_vals[0]],
        theta=score_cats + [score_cats[0]],
        fill="toself",
        line=dict(color=RED, width=2),
        fillcolor="rgba(255,0,0,0.1)",
        name="Channel Score"))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100], gridcolor="#222", tickfont=dict(color="#444")),
            angularaxis=dict(gridcolor="#222"),
            bgcolor=PAPER_BG),
        paper_bgcolor=PAPER_BG, height=380, font=dict(color=FONT_CLR),
        margin=dict(l=40,r=40,t=40,b=40),
        title=dict(text=f"Overall Score: {overall}/100", font=dict(family="Bebas Neue",size=22,color="#fff"), x=0.5),
        showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

grade = "S" if overall>=85 else "A" if overall>=70 else "B" if overall>=55 else "C" if overall>=40 else "D"
grade_color = "#ff0000" if grade in ["S","A"] else "#ff8800" if grade=="B" else "#888"
st.markdown(f"""
<div style="background:linear-gradient(135deg,#0f0f0f,#1a0000);border:1px solid #2a0000;border-radius:12px;padding:2rem;margin-top:1rem;display:flex;align-items:center;gap:2rem">
    <div style="font-family:'Bebas Neue';font-size:6rem;color:{grade_color};line-height:1">{grade}</div>
    <div>
        <div style="font-family:'Bebas Neue';font-size:1.8rem;letter-spacing:3px;color:#fff">CHANNEL GRADE · {overall}/100</div>
        <div style="color:#666;font-size:0.85rem;margin-top:6px;line-height:1.7">
            Top metric: <span style="color:#fff">{max(scores, key=scores.get)} ({max(score_vals)})</span> · 
            Needs work: <span style="color:#ff4444">{min(scores, key=scores.get)} ({min(score_vals)})</span>
        </div>
        <div style="margin-top:10px">
            {''.join([f'<span class="pill">{k}: {v}</span>' for k,v in scores.items()])}
        </div>
    </div>
</div>""", unsafe_allow_html=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────────
st.markdown("""
<hr class="yt-divider">
<div style="text-align:center;padding:2rem;color:#333;font-size:0.7rem;letter-spacing:2px;text-transform:uppercase">
    YT DeepDive · Channel Intelligence Platform · 20 Advanced Insights · Powered by YouTube Data API v3
</div>""", unsafe_allow_html=True)
