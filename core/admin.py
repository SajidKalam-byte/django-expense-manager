from django.contrib import admin
from .models import ProjectMeta


@admin.register(ProjectMeta)
class ProjectMetaAdmin(admin.ModelAdmin):
	list_display = ('total_budget', 'start_date', 'target_end_date')
