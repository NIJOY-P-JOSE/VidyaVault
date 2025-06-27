from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, Project, Comment, ProjectScore


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'domain', 'score', 'views', 'created_at', 'is_featured']
    list_filter = ['domain', 'is_featured', 'created_at']
    search_fields = ['title', 'description', 'owner__username']
    filter_horizontal = ['team_members', 'likes']
    readonly_fields = ['views', 'created_at', 'updated_at']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['project', 'author', 'created_at', 'parent']
    list_filter = ['created_at']
    search_fields = ['content', 'author__username', 'project__title']


@admin.register(ProjectScore)
class ProjectScoreAdmin(admin.ModelAdmin):
    list_display = ['project', 'reviewer', 'get_total_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['project__title', 'reviewer__username']


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)