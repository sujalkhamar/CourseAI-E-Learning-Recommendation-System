# 🎓 CourseAI — E-Learning Recommendation System

A full-stack Django web application that recommends Coursera courses using AI/ML techniques.

## 🚀 Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Django 4.2 |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn (TF-IDF, Cosine Similarity) |
| Visualization | Matplotlib, Seaborn |
| Dataset | Coursera Courses (3,522 courses, 184 universities) |

## 📁 Project Structure

```
elearning/
├── elearning/            # Django project settings & URLs
│   ├── settings.py
│   └── urls.py
├── recommender/          # Main app
│   ├── ml_engine.py      # ← Core AI/ML logic
│   ├── views.py          # Request handlers
│   ├── urls.py           # App URL routing
│   ├── Coursera.csv      # Dataset
│   └── templates/
│       └── recommender/
│           ├── base.html
│           ├── home.html
│           ├── results.html
│           ├── analytics.html
│           └── explore.html
├── requirements.txt
└── manage.py
```

## ⚙️ Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply migrations
python manage.py migrate

# 4. Run the development server
python manage.py runserver

# 5. Open in browser
# http://127.0.0.1:8000/
```

## 🧠 How the ML Algorithm Works

### Step 1 — Data Preprocessing
- Load `Coursera.csv` with Pandas
- Clean `Skills` column: remove special characters, lowercase, tokenize
- Normalize `Course Rating` to 0–1 range
- Fill missing ratings with column mean

### Step 2 — TF-IDF Vectorization
```python
from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(df['Skills'])
```
- Converts all course skill strings into a TF-IDF matrix
- TF (Term Frequency) × IDF (Inverse Document Frequency) gives weight to meaningful/rare skills

### Step 3 — Cosine Similarity
```python
from sklearn.metrics.pairwise import cosine_similarity
user_tfidf = vectorizer.transform([user_skills_string])
cosine_similarities = cosine_similarity(user_tfidf, tfidf_matrix)
```
- Transforms user's entered skills using the same vectorizer
- Computes similarity between user skills vector and every course's skill vector

### Step 4 — Final Scoring (Weighted Formula)
```
Final Score = (Cosine Similarity × 0.5)
            + (Normalized Rating   × 0.3)
            + (Difficulty Match    × 0.2)
```
- **50%** — Skill similarity (cosine similarity)
- **30%** — Course quality (normalized rating)
- **20%** — Difficulty preference match

### Step 5 — Ranking & Output
- Sort by Final Score descending
- Remove duplicates
- Return top-N courses

## 📊 Pages

| Page | URL | Description |
|------|-----|-------------|
| Home | `/` | Overview + quick recommendation form |
| Recommend | `/recommend/` | Submit skills, get ranked results |
| Explore | `/explore/` | Browse & filter all 3,522 courses |
| Analytics | `/analytics/` | Charts: rating dist., difficulty, top universities |

## 🔌 API Endpoint

`GET /api/skills/?q=<query>` — Autocomplete skill suggestions (JSON)

## 📈 Dataset

- **Source:** Coursera Courses Dataset 2021 (Kaggle)
- **Rows:** 3,522 courses
- **Columns:** Course Name, University, Difficulty Level, Course Rating, Course URL, Course Description, Skills
- **Universities:** 184 unique institutions

## 👨‍💻 Final Year Project

Built as a Final Year Project demonstrating:
- Web application development with Django
- Data science workflow with Pandas & NumPy
- NLP-based recommendation using TF-IDF
- ML similarity computation with Scikit-learn
- Data visualization with Matplotlib & Seaborn
- Responsive dark-themed UI
