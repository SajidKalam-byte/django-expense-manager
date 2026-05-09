import json
from datetime import date
from django.utils.timezone import now
from django.views.generic import TemplateView
from django.db.models import Sum
from django.db.models.functions import Coalesce, TruncMonth
from decimal import Decimal
from expenses.models import Expense
from wallets.models import Wallet
from .services import compute_project_metrics
from .forms import ProjectMetaForm
from django.shortcuts import redirect

class DashboardView(TemplateView):
    template_name = 'core/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from .services import compute_project_metrics
        context['analytics_metrics'] = compute_project_metrics()
        
        expenses = Expense.objects.select_related('category', 'wallet', 'vendor').order_by('-created_at')
        context['recent_expenses'] = expenses[:5]
        context['wallets'] = Wallet.objects.all()

        # 1. Total Spent (Coalesce protection)
        total = expenses.aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
        context['total_spent'] = float(total)

        # 2. Today's Spend
        today_total = expenses.filter(date=date.today()).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
        context['today_spend'] = float(today_total)

        # 3. This Month Spend
        current_now = now()
        month_total = expenses.filter(
            date__month=current_now.month,
            date__year=current_now.year
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
        context['this_month_spent'] = float(month_total)

        # 4. Top Category
        top_cat = expenses.values('category__name') \
            .annotate(total=Sum('amount')) \
            .exclude(category__name__isnull=True) \
            .order_by('-total') \
            .first()
        context['top_category'] = top_cat['category__name'] if top_cat else "None"

        # 5. Category Pie Chart Data
        category_data = expenses.values('category__name') \
            .annotate(total=Sum('amount')) \
            .exclude(category__name__isnull=True)
            
        cat_labels = [str(x['category__name']) for x in category_data]
        cat_values = [float(x['total']) for x in category_data]
        
        context['cat_labels_json'] = json.dumps(cat_labels)
        context['cat_values_json'] = json.dumps(cat_values)

        # 6. Trend Line Chart Data (Monthly)
        monthly_data = expenses.annotate(month=TruncMonth('date')) \
            .values('month') \
            .annotate(total=Sum('amount')) \
            .order_by('month')

        trend_labels = []
        for x in monthly_data:
            m = x['month']
            if not m:
                trend_labels.append("Unknown")
            elif isinstance(m, str):
                trend_labels.append(m[:7])
            else:
                trend_labels.append(m.strftime("%b %Y"))

        trend_values = [float(x['total']) for x in monthly_data]

        context['trend_labels_json'] = json.dumps(trend_labels)
        context['trend_values_json'] = json.dumps(trend_values)

        # 7. Labor vs Material (This Month)
        labor_total = expenses.filter(
            category__name='Labor',
            date__month=current_now.month,
            date__year=current_now.year
        ).aggregate(total=Coalesce(Sum('amount'), Decimal('0.00')))['total']
        
        labor_spend = float(labor_total)
        material_spend = float(month_total) - labor_spend
        
        if month_total > 0:
            labor_pct = int((labor_spend / float(month_total)) * 100)
            material_pct = 100 - labor_pct
        else:
            labor_pct = 0
            material_pct = 0

        context['labor_spend'] = labor_spend
        context['material_spend'] = material_spend
        context['labor_pct'] = labor_pct
        context['material_pct'] = material_pct

        return context

class AnalyticsView(TemplateView):
    template_name = 'core/analytics.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        metrics = compute_project_metrics()
        context['metrics'] = metrics
        
        if metrics and metrics.get('meta'):
            context['form'] = ProjectMetaForm(instance=metrics['meta'])
        else:
            context['form'] = ProjectMetaForm()
            
        return context

    def post(self, request, *args, **kwargs):
        from .models import ProjectMeta
        meta = ProjectMeta.objects.first()
        form = ProjectMetaForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            return redirect('core:analytics')
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)
