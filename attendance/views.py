from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse, HttpResponseRedirect
from .models import Attendance, WorkType
from .forms import AttendanceForm, WorkTypeForm
from .services import create_attendance, update_attendance, delete_attendance

from django.db.models import Sum, Avg, Q
from datetime import date, timedelta
import calendar

class AttendanceListView(ListView):
    model = Attendance
    template_name = 'attendance/attendance_list.html'
    context_object_name = 'attendances'
    ordering = ['-date', '-created_at']
    paginate_by = 10 # Paginate by 10 days instead of 25 rows

    def get_filtered_queryset(self):
        qs = Attendance.objects.select_related('work_type', 'wallet', 'linked_expense').all()
        
        # Date filtering
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date:
            qs = qs.filter(date__gte=start_date)
        if end_date:
            qs = qs.filter(date__lte=end_date)
            
        # Category/WorkType filter
        work_type = self.request.GET.get('work_type')
        if work_type:
            qs = qs.filter(work_type_id=work_type)
            
        # Phase filter
        phase = self.request.GET.get('phase')
        if phase:
            qs = qs.filter(phase=phase)
            
        # Search query
        query = self.request.GET.get('q')
        if query:
            qs = qs.filter(
                Q(custom_work_note__icontains=query) | 
                Q(work_type__name__icontains=query)
            )
            
        return qs.order_by('-date', '-created_at')

    def get_queryset(self):
        qs = self.get_filtered_queryset()
        
        # Group by date
        from decimal import Decimal
        grouped_data = []
        current_date = None
        current_group = None
        
        for entry in qs:
            if entry.date != current_date:
                if current_group:
                    grouped_data.append(current_group)
                current_date = entry.date
                current_group = {
                    'date': entry.date,
                    'entries': [],
                    'total_workers': 0,
                    'total_cost': Decimal('0.00')
                }
            
            current_group['entries'].append(entry)
            current_group['total_workers'] += entry.workers_count
            current_group['total_cost'] += entry.total_amount
            
        if current_group:
            grouped_data.append(current_group)
            
        return grouped_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        raw_qs = self.get_filtered_queryset()
        
        # Aggregations
        aggregates = raw_qs.aggregate(
            total_cost=Sum('total_amount'),
            total_workers=Sum('workers_count'),
            avg_wage=Avg('wage_per_worker')
        )
        context.update(aggregates)
        
        # Filter dropdown data
        context['work_types'] = WorkType.objects.all()
        context['phases'] = Attendance.objects.exclude(phase__isnull=True).exclude(phase='').values_list('phase', flat=True).distinct()
        
        # Current date context for quick filters
        today = date.today()
        context['today_str'] = today.isoformat()
        
        # Week range
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        context['week_start_str'] = start_of_week.isoformat()
        context['week_end_str'] = end_of_week.isoformat()
        
        # Month range
        start_of_month = today.replace(day=1)
        _, last_day = calendar.monthrange(today.year, today.month)
        end_of_month = today.replace(day=last_day)
        context['month_start_str'] = start_of_month.isoformat()
        context['month_end_str'] = end_of_month.isoformat()
        
        # Last 30 days
        context['last_30_days_str'] = (today - timedelta(days=30)).isoformat()
        
        return context

class AttendanceExportView(AttendanceListView):
    template_name = 'attendance/attendance_export.html'
    paginate_by = None

def get_work_type_wage(request):
    """ API endpoint for JS to accurately auto-fill wage without page reload """
    wt_id = request.GET.get('id')
    try:
        wt = WorkType.objects.get(id=wt_id)
        return JsonResponse({'wage': str(wt.default_wage)})
    except Exception:
        return JsonResponse({'wage': ''}, status=404)

class AttendanceCreateView(CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:list')

    def form_valid(self, form):
        try:
            create_attendance(form.cleaned_data)
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class AttendanceUpdateView(UpdateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance/attendance_form.html'
    success_url = reverse_lazy('attendance:list')

    def form_valid(self, form):
        try:
            attendance = self.get_object()
            update_attendance(attendance, form.cleaned_data)
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)

class AttendanceDeleteView(DeleteView):
    model = Attendance
    template_name = 'attendance/attendance_confirm_delete.html'
    success_url = reverse_lazy('attendance:list')

    def form_valid(self, form):
        attendance = self.get_object()
        delete_attendance(attendance)
        return HttpResponseRedirect(self.success_url)


class WorkTypeCreateView(CreateView):
    model = WorkType
    form_class = WorkTypeForm
    template_name = 'attendance/worktype_form.html'
    success_url = reverse_lazy('attendance:create')
