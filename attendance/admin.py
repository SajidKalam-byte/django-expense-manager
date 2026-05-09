from django.contrib import admin
from .models import Attendance, WorkType


@admin.register(WorkType)
class WorkTypeAdmin(admin.ModelAdmin):
	list_display = ('name', 'default_wage')
	search_fields = ('name',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
	list_display = ('date', 'work_type', 'workers_count', 'wage_per_worker', 'total_amount', 'wallet', 'phase')
	list_filter = ('date', 'work_type', 'wallet', 'phase', 'is_half_day')
	search_fields = ('custom_work_note',)
