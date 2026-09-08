from django.shortcuts import render
from django.http import JsonResponse
from .ml_engine import (
    get_recommendations, get_difficulty_distribution,
    get_rating_distribution, get_top_universities,
    get_avg_rating_by_difficulty, get_recommendation_chart,
    get_dataset_stats, ALL_SKILLS, DIFFICULTY_LEVELS, df
)

def home(request):
    stats = get_dataset_stats()
    return render(request, 'recommender/home.html', {
        'stats': stats,
        'difficulty_levels': DIFFICULTY_LEVELS,
        'popular_skills': stats['top_skills'][:30],
    })

def recommend(request):
    if request.method == 'POST':
        skills_input = request.POST.get('skills', '')
        difficulty = request.POST.get('difficulty', 'All')
        top_n = int(request.POST.get('top_n', 10))

        user_skills = [s.strip() for s in skills_input.split(',') if s.strip()]

        recommendations = get_recommendations(user_skills, difficulty, top_n)
        chart = get_recommendation_chart(recommendations) if recommendations else None

        return render(request, 'recommender/results.html', {
            'recommendations': recommendations,
            'user_skills': user_skills,
            'difficulty': difficulty,
            'chart': chart,
            'count': len(recommendations),
            'difficulty_levels': DIFFICULTY_LEVELS,
        })
    return render(request, 'recommender/home.html')

def analytics(request):
    diff_chart = get_difficulty_distribution()
    rating_chart = get_rating_distribution()
    uni_chart = get_top_universities()
    avg_chart = get_avg_rating_by_difficulty()
    stats = get_dataset_stats()

    return render(request, 'recommender/analytics.html', {
        'diff_chart': diff_chart,
        'rating_chart': rating_chart,
        'uni_chart': uni_chart,
        'avg_chart': avg_chart,
        'stats': stats,
    })

def explore(request):
    difficulty = request.GET.get('difficulty', 'All')
    search = request.GET.get('search', '')
    sort = request.GET.get('sort', 'rating')

    filtered = df.copy()
    if difficulty != 'All':
        filtered = filtered[filtered['difficulty'] == difficulty]
    if search:
        filtered = filtered[
            filtered['course_name'].str.contains(search, case=False, na=False) |
            filtered['university'].str.contains(search, case=False, na=False) |
            filtered['skills'].str.contains(search, case=False, na=False)
        ]
    if sort == 'rating':
        filtered = filtered.sort_values('rating', ascending=False)
    elif sort == 'name':
        filtered = filtered.sort_values('course_name')

    courses = filtered[['course_name', 'university', 'difficulty',
                         'rating', 'url', 'skills']].head(50).to_dict('records')

    return render(request, 'recommender/explore.html', {
        'courses': courses,
        'difficulty_levels': DIFFICULTY_LEVELS,
        'selected_difficulty': difficulty,
        'search': search,
        'sort': sort,
        'total': len(filtered),
    })

def autocomplete_skills(request):
    q = request.GET.get('q', '').lower()
    if len(q) < 2:
        return JsonResponse({'skills': []})
    matches = [s for s in ALL_SKILLS if q in s][:15]
    return JsonResponse({'skills': matches})
