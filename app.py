import streamlit as st
import pickle
import pandas as pd
import requests

def fetch_genre(id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=1a9dc8c94fa5574c39e628dab6f547e8&language=en-US')
    data = response.json()
    genres = ", ".join([genre['name'] for genre in data['genres']])
    return genres

def fetch_rating(id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=1a9dc8c94fa5574c39e628dab6f547e8&language=en-US')
    data = response.json()
    return data['vote_average']

def fetch_trailer(id):
    response = requests.get(
        f'https://api.themoviedb.org/3/movie/{id}/videos?api_key=1a9dc8c94fa5574c39e628dab6f547e8&language=en-US'
    )
    data = response.json()
    for video in data['results']:
        if video['type'] == 'Trailer' and video['site'] == 'YouTube':
            return f"https://www.youtube.com/watch?v={video['key']}"
    return None


def fetch_details(id):
    response = requests.get(f'https://api.themoviedb.org/3/movie/{id}?api_key=1a9dc8c94fa5574c39e628dab6f547e8&language=en-US')
    data = response.json()
    return data['overview']

def fetch_poster(id):
    response = requests.get('https://api.themoviedb.org/3/movie/{}?api_key=1a9dc8c94fa5574c39e628dab6f547e8&language=en-US'.format(id))
    data = response.json()
    return "https://image.tmdb.org/t/p/w500/"+data['poster_path']


def recommend(movie):
    index = movies[movies['title']==movie].index[0]
    distances = similarity[index]
    movieList = sorted(list(enumerate(distances)),reverse=True,key = lambda x:x[1])[1:6]
    recommended = []
    recommended_poster=[]
    recommended_overview=[]
    genre = []
    rating = []
    trailer = []
    for i in movieList:
        recommended.append(movies.iloc[i[0]].title)
        recommended_poster.append(fetch_poster(movies.iloc[i[0]].id))
        recommended_overview.append(fetch_details(movies.iloc[i[0]].id))
        genre.append(fetch_genre(movies.iloc[i[0]].id))
        rating.append(fetch_rating(movies.iloc[i[0]].id))
        trailer.append(fetch_trailer(movies.iloc[i[0]].id))
    return recommended, recommended_poster,recommended_overview , rating , trailer,genre

similarity = pickle.load(open('similarity.pkl', 'rb'))


movie_list = pickle.load(open('movies_dict.pkl', 'rb'))
movies  = pd.DataFrame(movie_list)

st.title("🎬 Movie Recommender System")

st.sidebar.title("🎥 Choose a Movie")
selected = st.sidebar.selectbox('Choose a Movie to Get Recommendations:', movies['title'].values)
recommend_clicked = st.sidebar.button('🎬 Recommend Movies')

if not recommend_clicked:
    # Show Welcome Page
    st.markdown("## 👋 Welcome to Movie Recommender!")
    st.image("image.png", use_container_width=True)
    st.markdown("""
        This app helps you discover movies similar to your favorite ones.

        - ✅ Browse movies
        - 🎞️ View genres, trailers, and ratings
        - ⭐ Get personalized recommendations

        Select a movie from the sidebar to get started!
    """)
else:
    name,poster, overview , rating ,trailer,genre = recommend(selected)
    st.markdown("## 📌 Selected Movie Details")
    selected_index = movies[movies['title'] == selected].index[0]
    selected_id = movies.iloc[selected_index].id

    col1, col2 = st.columns([1, 2])
    with col1:
        st.image(fetch_poster(selected_id))
    with col2:
        st.subheader(selected)
        st.markdown(f"**⭐ Rating:** {fetch_rating(selected_id)}/10")
        st.markdown(f"**🎬 Genre:** {fetch_genre(selected_id)}")
        st.markdown(f"**Description:** {fetch_details(selected_id)}")
        trailer_link = fetch_trailer(selected_id)
        if trailer_link:
            st.link_button("▶ Watch Trailer", trailer_link)

    st.markdown("---")
    st.subheader("📽️ Recommended Movies")
    for i in range(0, 5, 2):  # Loop in steps of 2
        cols = st.columns(2)  # 2 columns per row
        for j in range(2):
            if i + j < 5:
                with cols[j]:
                    st.header(name[i + j])
                    st.image(poster[i + j], use_container_width=True)
                    st.markdown(f"**⭐ Rating:** {rating[i + j]}/10")
                    st.markdown(f"**🎬 Genre:**   {genre[i + j]}/10")
                    st.markdown(f"**Description:**   {overview[i + j]}/10")
                    if trailer[i + j]:
                        st.link_button("▶ Watch Trailer", trailer[i + j])
                    else:
                        st.caption("🎥 Trailer not available ")