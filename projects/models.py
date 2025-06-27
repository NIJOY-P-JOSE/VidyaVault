from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('admin', 'Admin/Faculty'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')
    batch = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=50, blank=True)
    github_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"
    
    def get_total_score(self):
        return sum(project.score for project in self.user.project_set.all() if project.score)
    
    def get_total_likes(self):
        return sum(project.likes.count() for project in self.user.project_set.all())


class Project(models.Model):
    DOMAIN_CHOICES = [
        ('web', 'Web Development'),
        ('mobile', 'Mobile Development'),
        ('ai_ml', 'AI/ML'),
        ('data_science', 'Data Science'),
        ('iot', 'IoT'),
        ('blockchain', 'Blockchain'),
        ('game', 'Game Development'),
        ('desktop', 'Desktop Application'),
        ('other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    team_members = models.ManyToManyField(User, related_name='team_projects', blank=True)
    domain = models.CharField(max_length=20, choices=DOMAIN_CHOICES)
    tech_stack = models.CharField(max_length=500, help_text="Comma-separated technologies")
    github_url = models.URLField(blank=True)
    project_file = models.FileField(upload_to='project_files/', blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    score = models.IntegerField(null=True, blank=True, help_text="Score from 1-10")
    is_featured = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    likes = models.ManyToManyField(User, related_name='liked_projects', blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'pk': self.pk})
    
    def get_tech_list(self):
        return [tech.strip() for tech in self.tech_stack.split(',') if tech.strip()]
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])


class Comment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Comment by {self.author.username} on {self.project.title}"


class ProjectScore(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='scores')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    innovation_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    completeness_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    design_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    github_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)])
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        unique_together = ['project', 'reviewer']
    
    def get_total_score(self):
        return (self.innovation_score + self.completeness_score + 
                self.design_score + self.github_score) / 4
    
    def __str__(self):
        return f"Score for {self.project.title} by {self.reviewer.username}"