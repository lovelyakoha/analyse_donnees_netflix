import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Analytics Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎬 Netflix Analytics Dashboard")
st.markdown("""
**Bienvenue sur l'outil d'exploration du catalogue Netflix.**
Cette application interactive permet d'analyser les tendances de contenus, la distribution géographique, les genres et les talents.
""")
st.markdown("---")

# --- 2. CHARGEMENT ET NETTOYAGE ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('data/netflix_titles.csv')
    except FileNotFoundError:
        df = pd.read_csv('../data/netflix_titles.csv')
    
    # Nettoyage
    df['director'] = df['director'].fillna('Unknown')
    df['cast'] = df['cast'].fillna('Unknown')
    df['country'] = df['country'].fillna('Unknown')
    df.dropna(subset=['date_added', 'rating', 'duration'], inplace=True)
    
    # Conversions
    df['date_added'] = pd.to_datetime(df['date_added'].str.strip())
    df['year_added'] = df['date_added'].dt.year
    df['month_added'] = df['date_added'].dt.month_name()
    
    # Extraction durée (Films)
    df['duration_min'] = df.apply(lambda x: int(x['duration'].split(' ')[0]) if x['type'] == 'Movie' else 0, axis=1)
    
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Erreur de chargement : {e}")
    st.stop()

# --- 3. FILTRES ---
st.sidebar.header("🔍 Filtres d'Analyse")
type_filter = st.sidebar.radio("Type de contenu", ["Tous", "Movie", "TV Show"])

min_year = int(df['year_added'].min())
max_year = int(df['year_added'].max())
selected_years = st.sidebar.slider("Période d'ajout", min_year, max_year, (2015, max_year))

# Application des filtres
df_filtered = df[(df['year_added'] >= selected_years[0]) & (df['year_added'] <= selected_years[1])]
if type_filter != "Tous":
    df_filtered = df_filtered[df_filtered['type'] == type_filter]

st.sidebar.markdown(f"**{df_filtered.shape[0]}** titres affichés")

# --- 4. DASHBOARD - KPI ---

# KPI Pays Uniques
all_countries = df_filtered['country'].str.split(', ', expand=True).stack()
unique_countries_count = all_countries[all_countries != 'Unknown'].nunique()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Titres Totaux", df_filtered.shape[0])
col2.metric("Films", df_filtered[df_filtered['type'] == 'Movie'].shape[0])
col3.metric("Séries TV", df_filtered[df_filtered['type'] == 'TV Show'].shape[0])
col4.metric("Pays Uniques", unique_countries_count)

st.markdown("---")

# --- 5. ANALYSES PRINCIPALES ---
st.header("📊 Vue d'ensemble")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Répartition Films vs Séries")
    fig_pie = px.pie(df_filtered, names='type', 
                     color_discrete_sequence=px.colors.sequential.RdBu, hole=0.4)
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("Top 10 des Pays Producteurs")
    country_series = df_filtered['country'].str.split(', ', expand=True).stack()
    country_series = country_series[country_series != 'Unknown']
    
    top_countries = country_series.value_counts().head(10).reset_index()
    top_countries.columns = ['Country', 'Count']
    
    fig_bar = px.bar(top_countries, x='Count', y='Country', orientation='h', 
                     text='Count', color='Count', color_continuous_scale='Viridis')
    fig_bar.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_bar, use_container_width=True)

# --- CARTE INTERACTIVE ---
st.subheader("Carte Mondiale des Contenus")
st.markdown("Visualisation de la densité de production par pays.")

# Préparation des données pour la carte (tous les pays)
country_counts = country_series.value_counts().reset_index()
country_counts.columns = ['Country', 'Count']

fig_map = px.choropleth(
    country_counts,
    locations='Country',
    locationmode='country names',
    color='Count',
    hover_name='Country',
    color_continuous_scale='Viridis',
    projection='natural earth',
    title='Nombre de titres par pays'
)
# Ajustement des marges pour que la carte soit grande
fig_map.update_layout(height=600, margin={"r":0,"t":50,"l":0,"b":0})
st.plotly_chart(fig_map, use_container_width=True)

st.markdown("---")

# --- 6. ANALYSE TEMPORELLE ---
st.subheader("Évolution du catalogue")
counts_year = df_filtered.groupby('year_added')['show_id'].count().reset_index(name='count')
fig_line = px.area(counts_year, x='year_added', y='count', markers=True,
                   labels={'year_added': 'Année', 'count': 'Titres ajoutés'})
st.plotly_chart(fig_line, use_container_width=True)

st.markdown("---")

# --- 7. GENRES & TALENTS ---
st.header("Genres & Talents")

# Top 20 Genres
st.subheader("Top 20 des Genres")
genres_series = df_filtered['listed_in'].str.split(', ', expand=True).stack()
top_genres = genres_series.value_counts().head(20).reset_index()
top_genres.columns = ['Genre', 'Count']

fig_genres = px.bar(top_genres, x='Count', y='Genre', orientation='h', 
                    color='Count', color_continuous_scale='Teal', text='Count')
fig_genres.update_layout(yaxis=dict(autorange="reversed"), height=600)
st.plotly_chart(fig_genres, use_container_width=True)

# Acteurs et Réalisateurs
col_cast, col_dir = st.columns(2)

with col_cast:
    st.subheader("Top 10 Acteurs")
    cast_series = df_filtered['cast'].str.split(', ', expand=True).stack()
    cast_series = cast_series[cast_series != 'Unknown']
    
    top_cast = cast_series.value_counts().head(10).reset_index()
    top_cast.columns = ['Actor', 'Count']
    
    fig_cast = px.bar(top_cast, x='Count', y='Actor', orientation='h',
                      color='Count', color_continuous_scale='Blues')
    fig_cast.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_cast, use_container_width=True)

with col_dir:
    st.subheader("Top 10 Réalisateurs")
    dir_series = df_filtered['director'].str.split(', ', expand=True).stack()
    dir_series = dir_series[dir_series != 'Unknown']
    
    top_dir = dir_series.value_counts().head(10).reset_index()
    top_dir.columns = ['Director', 'Count']
    
    fig_dir = px.bar(top_dir, x='Count', y='Director', orientation='h',
                     color='Count', color_continuous_scale='Reds')
    fig_dir.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_dir, use_container_width=True)

st.markdown("---")

# --- 8. ANALYSES COMPLÉMENTAIRES ---
st.header("🔬 Analyses Approfondies")
tab1, tab2, tab3 = st.tabs(["Durée des Films", "Saisonnalité", "Nuage de Mots"])

with tab1:
    st.subheader("Distribution de la durée des films")
    if type_filter == "TV Show":
        st.warning("Sélectionnez 'Tous' ou 'Movie' pour voir la durée.")
    else:
        fig_box, ax = plt.subplots(figsize=(10, 4))
        movies_only = df_filtered[df_filtered['type'] == 'Movie']
        sns.boxplot(x=movies_only['duration_min'], color='skyblue', ax=ax)
        ax.set_xlabel("Durée (minutes)")
        st.pyplot(fig_box)

with tab2:
    st.subheader("Meilleur mois pour les sorties")
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                   'July', 'August', 'September', 'October', 'November', 'December']
    fig_month, ax = plt.subplots(figsize=(10, 4))
    sns.countplot(x='month_added', data=df_filtered, order=month_order, palette='viridis', ax=ax)
    plt.xticks(rotation=45)
    ax.set_xlabel("")
    st.pyplot(fig_month)

with tab3:
    st.subheader("Nuage de mots des Genres")
    if st.button("Générer le Nuage"):
        text = ' '.join(df_filtered['listed_in'].dropna())
        wordcloud = WordCloud(width=800, height=400, background_color='black', colormap='Reds').generate(text)
        fig_wc, ax = plt.subplots(figsize=(12, 6))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig_wc)

st.caption("Application Streamlit • Analyse Netflix")