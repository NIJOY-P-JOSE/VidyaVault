from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Avg, Q
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from .models import Project, UserProfile, Comment, ProjectScore
from .forms import ProjectForm, UserRegistrationForm, CommentForm, ProjectScoreForm
from collections import Counter
import json
import os
import base64
import requests
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .chatbot_gemini import ask_gemini


def chatbot_view(request):
    response = None
    if request.method == "POST":
        prompt = request.POST.get("prompt")
        response = ask_gemini(prompt)

    return render(request, "chatbot.html", {"response": response})


def fetch_github_readme(project):
    try:
        github_url = project.github_url
        description = project.description or "No description available."

        repo_api_url = github_url.replace("https://github.com", "https://api.github.com/repos")
        readme_url = f"{repo_api_url}/contents/README.md"
        contents_url = f"{repo_api_url}/contents"

        headers = {
            "Accept": "application/vnd.github.v3+json"
        }

        github_token = os.getenv("GITHUB_API_TOKEN")
        if github_token:
            headers["Authorization"] = f"Bearer {github_token}"

        # README content
        readme_text = ""
        response = requests.get(readme_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            readme_text = base64.b64decode(data['content']).decode('utf-8')
        else:
            readme_text = f"(README not available — GitHub returned {response.status_code})"

        # Top-level files
        files_response = requests.get(contents_url, headers=headers)
        project_code_snippets = ""
        if files_response.status_code == 200:
            files = files_response.json()
            important_extensions = ['.py', '.html', '.js', '.css']
            MAX_FILES = 5
            MAX_LINES = 50
            files_added = 0

            for file in files:
                if files_added >= MAX_FILES:
                    break
                name = file["name"]
                ext = os.path.splitext(name)[1].lower()
                if ext not in important_extensions:
                    continue
                if file.get("size", 0) > 50 * 1024:
                    continue
                raw_url = file.get("download_url")
                if not raw_url:
                    continue
                raw_response = requests.get(raw_url)
                if raw_response.status_code == 200:
                    lines = raw_response.text.splitlines()
                    content = "\n".join(lines[:MAX_LINES])
                    project_code_snippets += f"\n\n--- {name} ---\n{content}"
                    files_added += 1

        # Final context
        full_context = f"Project Description:\n{description}\n\nREADME Content:\n{readme_text}\n\nSample Code Files:{project_code_snippets}"
        return full_context

    except Exception as e:
        return f"(Error fetching GitHub content: {e})"


# Call AI model with context
def call_ai_model(question, context):
    prompt = f"Context:\n{context}\n\nQuestion: {question}\nAnswer:"
    return ask_gemini(prompt)


# This function builds context from GitHub, adds user question, and gets AI answer
@csrf_exempt
def project_chatbot(request, project_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            question = data.get("question", "").strip()

            if not question:
                return JsonResponse({"answer": "Please enter a valid question."})

            # ✅ Get project object
            project = Project.objects.get(id=project_id)

            # ✅ Get context (README + sample code)
            from .views import fetch_github_readme  # or move fetch_github_readme to utils
            context = fetch_github_readme(project)

            # ✅ Final prompt = context + user question
            full_prompt = f"{context}\n\nUser question: {question}"

            # ✅ Call Gemini AI
            answer = ask_gemini(full_prompt)

            return JsonResponse({"answer": answer})

        except Project.DoesNotExist:
            return JsonResponse({"answer": "Project not found."}, status=404)
        except Exception as e:
            return JsonResponse({"answer": f"Error occurred: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


def home(request):
    # Get statistics for charts
    featured_projects = Project.objects.filter(is_featured=True)[:6]
    top_students = User.objects.annotate(
        total_score=Count('project__score')
    ).order_by('-total_score')[:5]
    
    recent_projects = Project.objects.all()[:8]
    
    context = {
        'featured_projects': featured_projects,
        'top_students': top_students,
        'recent_projects': recent_projects,
    }
    return render(request, 'projects/home.html', context)


def about(request):
    return render(request, 'projects/about.html')


@login_required
def dashboard(request):
    user_projects = Project.objects.filter(owner=request.user)
    recent_projects = Project.objects.all()[:5]
    
    context = {
        'user_projects': user_projects,
        'recent_projects': recent_projects,
    }
    return render(request, 'projects/dashboard.html', context)


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                batch=form.cleaned_data.get('batch'),
                department=form.cleaned_data.get('department')
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('dashboard')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


def project_list(request):
    projects = Project.objects.all()
    
    # Filtering
    domain = request.GET.get('domain')
    tech = request.GET.get('tech')
    search = request.GET.get('search')
    
    if domain:
        projects = projects.filter(domain=domain)
    if tech:
        projects = projects.filter(tech_stack__icontains=tech)
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(tech_stack__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(projects, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get unique technologies for filter
    all_techs = []
    for project in Project.objects.all():
        all_techs.extend(project.get_tech_list())
    unique_techs = sorted(set(all_techs))
    
    context = {
        'page_obj': page_obj,
        'domain_choices': Project.DOMAIN_CHOICES,
        'unique_techs': unique_techs,
        'current_domain': domain,
        'current_tech': tech,
        'current_search': search,
    }
    return render(request, 'projects/project_list.html', context)


def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    project.increment_views()
    
    comments = project.comments.filter(parent=None)
    comment_form = CommentForm()
    
    # Check if user has liked this project
    user_has_liked = False
    if request.user.is_authenticated:
        user_has_liked = project.likes.filter(id=request.user.id).exists()
    
    context = {
        'project': project,
        'comments': comments,
        'comment_form': comment_form,
        'user_has_liked': user_has_liked,
    }
    return render(request, 'projects/project_detail.html', context)


@login_required
def upload_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            form.save_m2m()  # Save many-to-many relationships
            messages.success(request, 'Project uploaded successfully!')
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'projects/upload_project.html', {'form': form})


@login_required
@require_POST
def toggle_like(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if project.likes.filter(id=request.user.id).exists():
        project.likes.remove(request.user)
        liked = False
    else:
        project.likes.add(request.user)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'likes_count': project.likes.count()
    })


@login_required
@require_POST
def add_comment(request, pk):
    project = get_object_or_404(Project, pk=pk)
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.project = project
        comment.author = request.user
        
        parent_id = request.POST.get('parent_id')
        if parent_id:
            comment.parent = get_object_or_404(Comment, id=parent_id)
        
        comment.save()
        messages.success(request, 'Comment added successfully!')
    
    return redirect('project_detail', pk=pk)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    user_projects = Project.objects.filter(owner=user)
    
    context = {
        'profile_user': user,
        'profile': profile,
        'user_projects': user_projects,
    }
    return render(request, 'projects/profile.html', context)


@login_required
def my_profile(request):
    return redirect('profile', username=request.user.username)


def leaderboard(request):
    # Get users with their total scores
    users_with_scores = []
    for user in User.objects.all():
        profile, created = UserProfile.objects.get_or_create(user=user)
        if profile.role == 'student':
            total_score = sum(p.score for p in user.project_set.all() if p.score)
            total_likes = sum(p.likes.count() for p in user.project_set.all())
            users_with_scores.append({
                'user': user,
                'profile': profile,
                'total_score': total_score,
                'total_likes': total_likes,
                'project_count': user.project_set.count()
            })
    
    # Sort by total score
    users_with_scores.sort(key=lambda x: x['total_score'], reverse=True)
    
    context = {
        'users_with_scores': users_with_scores[:50]  # Top 50
    }
    return render(request, 'projects/leaderboard.html', context)


@login_required
def admin_review(request):
    # Check if user is admin
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    # Get projects that need review (no score yet)
    projects_to_review = Project.objects.filter(score__isnull=True)
    
    context = {
        'projects_to_review': projects_to_review,
    }
    return render(request, 'projects/admin_review.html', context)


@login_required
def score_project(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    # Check if user is admin
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if profile.role != 'admin':
        messages.error(request, 'Access denied. Admin privileges required.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProjectScoreForm(request.POST)
        if form.is_valid():
            score_obj = form.save(commit=False)
            score_obj.project = project
            score_obj.reviewer = request.user
            score_obj.save()
            
            # Update project score
            project.score = int(score_obj.get_total_score())
            project.save()
            
            messages.success(request, 'Project scored successfully!')
            return redirect('admin_review')
    else:
        form = ProjectScoreForm()
    
    context = {
        'project': project,
        'form': form,
    }
    return render(request, 'projects/score_project.html', context)


# API Views for Charts
def department_stats(request):
    stats = UserProfile.objects.values('department').annotate(
        count=Count('department'),
        avg_score=Avg('user__project__score')
    ).exclude(department='')
    
    return JsonResponse(list(stats), safe=False)


def tech_stats(request):
    all_techs = []
    for project in Project.objects.all():
        all_techs.extend(project.get_tech_list())
    
    tech_counts = Counter(all_techs)
    stats = [{'tech': tech, 'count': count} for tech, count in tech_counts.most_common(10)]
    
    return JsonResponse(stats, safe=False)


def user_skills(request, username):
    user = get_object_or_404(User, username=username)
    user_projects = Project.objects.filter(owner=user)
    
    all_techs = []
    for project in user_projects:
        all_techs.extend(project.get_tech_list())
    
    tech_counts = Counter(all_techs)
    skills = [{'skill': tech, 'count': count} for tech, count in tech_counts.items()]
    
    return JsonResponse(skills, safe=False)
