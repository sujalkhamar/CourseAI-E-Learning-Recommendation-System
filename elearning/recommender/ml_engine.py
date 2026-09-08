import pandas as pd
import numpy as np
import re
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
import io, base64

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, 'Coursera.csv')

# ─── Load & Preprocess ───────────────────────────────────────────────
def load_data():
    df = pd.read_csv(CSV_PATH)
    df.rename(columns={
        'Course Name': 'course_name',
        'University': 'university',
        'Difficulty Level': 'difficulty',
        'Course Rating': 'rating',
        'Course URL': 'url',
        'Course Description': 'description',
        'Skills': 'skills',
    }, inplace=True)
    df['rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df['rating'] = df['rating'].fillna(df['rating'].mean())
    df['normalized_rating'] = df['rating'] / 5.0

    def preprocess_skills(skill):
        if isinstance(skill, str):
            skill = re.sub(r'[^\w\s-]', '', skill)
            return ' '.join(skill.lower().split())
        return 'no_skills'

    df['skills'] = df['skills'].apply(preprocess_skills)
    df['skills'] = df['skills'].apply(lambda x: x if len(x.strip()) > 0 else 'no_skills')
    df['difficulty'] = df['difficulty'].fillna('Beginner')
    return df

df = load_data()

vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['skills'])

DIFFICULTY_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Mixed']
ALL_SKILLS = sorted(set(
    word for skills in df['skills']
    for word in skills.split()
    if word != 'no_skills' and len(word) > 2
))

# ─── Recommendation Engine ────────────────────────────────────────────
def get_recommendations(user_skills, difficulty='All', top_n=10):
    if not user_skills:
        return []
    user_str = ' '.join([s.lower().strip() for s in user_skills])
    user_tfidf = vectorizer.transform([user_str])
    cosine_similarities = cosine_similarity(user_tfidf, tfidf_matrix).flatten()

    temp_df = df.copy()
    temp_df['cosine_similarity'] = cosine_similarities

    cosine_weight = 0.5
    rating_weight = 0.3
    difficulty_weight = 0.2

    def compute_final_score(row):
        d_score = 1 if (difficulty == 'All' or row['difficulty'] == difficulty) else 0
        return (row['cosine_similarity'] * cosine_weight +
                row['normalized_rating'] * rating_weight +
                d_score * difficulty_weight)

    temp_df['final_score'] = temp_df.apply(compute_final_score, axis=1)

    if difficulty != 'All':
        temp_df = temp_df[temp_df['difficulty'] == difficulty]

    results = (temp_df[['course_name', 'university', 'difficulty',
                         'rating', 'url', 'skills',
                         'cosine_similarity', 'final_score']]
               .sort_values('final_score', ascending=False)
               .drop_duplicates(subset=['course_name'])
               .head(top_n))
    return results.to_dict('records')

# ─── Statistics & Charts ─────────────────────────────────────────────
def fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=120, facecolor='#0f172a')
    buf.seek(0)
    img = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return img

CHART_STYLE = {
    'figure.facecolor': '#0f172a',
    'axes.facecolor': '#1e293b',
    'axes.edgecolor': '#334155',
    'axes.labelcolor': '#94a3b8',
    'xtick.color': '#94a3b8',
    'ytick.color': '#94a3b8',
    'text.color': '#e2e8f0',
    'grid.color': '#334155',
}

def get_difficulty_distribution():
    plt.rcParams.update(CHART_STYLE)
    counts = df['difficulty'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 5))
    colors = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd']
    wedges, texts, autotexts = ax.pie(counts.values, labels=counts.index,
                                       autopct='%1.1f%%', colors=colors,
                                       textprops={'color': '#e2e8f0', 'fontsize': 11})
    for at in autotexts:
        at.set_color('#0f172a')
        at.set_fontweight('bold')
    ax.set_title('Courses by Difficulty Level', color='#e2e8f0', fontsize=14, pad=15)
    return fig_to_base64(fig)

def get_rating_distribution():
    plt.rcParams.update(CHART_STYLE)
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(df['rating'].dropna(), bins=20, color='#6366f1', edgecolor='#818cf8', alpha=0.85)
    ax.set_xlabel('Course Rating', fontsize=12)
    ax.set_ylabel('Number of Courses', fontsize=12)
    ax.set_title('Distribution of Course Ratings', color='#e2e8f0', fontsize=14)
    ax.grid(True, alpha=0.3)
    return fig_to_base64(fig)

def get_top_universities():
    plt.rcParams.update(CHART_STYLE)
    top_uni = df['university'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.barh(top_uni.index[::-1], top_uni.values[::-1],
                   color=['#6366f1', '#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd',
                          '#6366f1', '#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd'])
    ax.set_xlabel('Number of Courses', fontsize=12)
    ax.set_title('Top 10 Universities on Coursera', color='#e2e8f0', fontsize=14)
    ax.grid(True, axis='x', alpha=0.3)
    for bar, val in zip(bars, top_uni.values[::-1]):
        ax.text(val + 0.5, bar.get_y() + bar.get_height()/2, str(val),
                va='center', color='#e2e8f0', fontsize=9)
    return fig_to_base64(fig)

def get_avg_rating_by_difficulty():
    plt.rcParams.update(CHART_STYLE)
    avg = df.groupby('difficulty')['rating'].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(6, 4))
    colors = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd']
    bars = ax.bar(avg.index, avg.values, color=colors[:len(avg)])
    ax.set_ylabel('Average Rating', fontsize=12)
    ax.set_title('Avg Rating by Difficulty', color='#e2e8f0', fontsize=14)
    ax.set_ylim(0, 5)
    ax.grid(True, axis='y', alpha=0.3)
    for bar, val in zip(bars, avg.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.03,
                f'{val:.2f}', ha='center', color='#e2e8f0', fontsize=10, fontweight='bold')
    return fig_to_base64(fig)

def get_recommendation_chart(recommendations):
    if not recommendations:
        return None
    plt.rcParams.update(CHART_STYLE)
    top = recommendations[:8]
    names = [r['course_name'][:35] + '...' if len(r['course_name']) > 35 else r['course_name'] for r in top]
    scores = [r['final_score'] for r in top]
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = plt.cm.Purples(np.linspace(0.5, 1.0, len(names)))
    bars = ax.barh(names[::-1], scores[::-1], color=colors)
    ax.set_xlabel('Final Score', fontsize=12)
    ax.set_title('Top Recommended Courses by Score', color='#e2e8f0', fontsize=14)
    ax.grid(True, axis='x', alpha=0.3)
    ax.set_xlim(0, 1)
    for bar, val in zip(bars, scores[::-1]):
        ax.text(val + 0.005, bar.get_y() + bar.get_height()/2, f'{val:.3f}',
                va='center', color='#e2e8f0', fontsize=9)
    return fig_to_base64(fig)

def get_dataset_stats():
    return {
        'total_courses': len(df),
        'total_universities': df['university'].nunique(),
        'avg_rating': round(df['rating'].mean(), 2),
        'difficulty_counts': df['difficulty'].value_counts().to_dict(),
        'top_skills': ALL_SKILLS[:50],
    }
