from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Project, Comment, ProjectScore


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    batch = forms.CharField(max_length=20, required=True, help_text="e.g., 2020-2024")
    department = forms.CharField(max_length=50, required=True, help_text="e.g., Computer Science")
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user


class ProjectForm(forms.ModelForm):
    team_members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Select team members (optional)"
    )
    
    class Meta:
        model = Project
        fields = ['title', 'description', 'domain', 'tech_stack', 'github_url', 'project_file', 'team_members']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter project title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Describe your project...'}),
            'domain': forms.Select(attrs={'class': 'form-select'}),
            'tech_stack': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Python, Django, JavaScript, React'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/username/repo'}),
            'project_file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your comment or question...'
            })
        }


class ProjectScoreForm(forms.ModelForm):
    class Meta:
        model = ProjectScore
        fields = ['innovation_score', 'completeness_score', 'design_score', 'github_score', 'comments']
        widgets = {
            'innovation_score': forms.Select(attrs={'class': 'form-select'}),
            'completeness_score': forms.Select(attrs={'class': 'form-select'}),
            'design_score': forms.Select(attrs={'class': 'form-select'}),
            'github_score': forms.Select(attrs={'class': 'form-select'}),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Additional feedback...'}),
        }