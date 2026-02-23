from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import DecimalField, Sum, F,ExpressionWrapper
from .models import Product, Category, Sale
from .forms import ProductForm, CategoryForm, SaleForm, RegisterForm
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('login')
    return render(request, 'register.html', {'form': form})


@login_required
def dashboard(request):

    total_products = Product.objects.count()
    total_categories = Category.objects.count()

    # Total quantity sold
    total_sales = Sale.objects.aggregate(
        Sum('quantity_sold')
    )['quantity_sold__sum'] or 0

    # Expression for revenue
    revenue_expression = ExpressionWrapper(
        F('quantity_sold') * F('product__price'),
        output_field=DecimalField()
    )

    # -----------------------------
    # TOTAL REVENUE
    # -----------------------------
    total_revenue = Sale.objects.aggregate(
        revenue=Sum(revenue_expression)
    )['revenue'] or 0

    # -----------------------------
    # TODAY REVENUE
    # -----------------------------
    today = timezone.now().date()

    today_revenue = Sale.objects.filter(
        sale_date__date=today
    ).aggregate(
        revenue=Sum(revenue_expression)
    )['revenue'] or 0

    # -----------------------------
    # WEEKLY REVENUE (Last 7 Days)
    # -----------------------------
    week_start = timezone.now() - timedelta(days=7)

    weekly_revenue = Sale.objects.filter(
        sale_date__gte=week_start
    ).aggregate(
        revenue=Sum(revenue_expression)
    )['revenue'] or 0

    # -----------------------------
    # MONTHLY REVENUE (Current Month)
    # -----------------------------
    monthly_revenue = Sale.objects.filter(
        sale_date__month=today.month,
        sale_date__year=today.year
    ).aggregate(
        revenue=Sum(revenue_expression)
    )['revenue'] or 0

    # -----------------------------
    # Monthly Chart Report
    # -----------------------------
    monthly_sales = (
        Sale.objects
        .annotate(month=TruncMonth('sale_date'))
        .values('month')
        .annotate(total=Sum(revenue_expression))
        .order_by('month')
    )

    chart_labels = []
    chart_data = []
    monthly_report = []

    for item in monthly_sales:
        month_name = item['month'].strftime("%B %Y")
        chart_labels.append(month_name)
        chart_data.append(float(item['total']))
        monthly_report.append({
            'month': month_name,
            'total': round(item['total'], 2)
        })

    context = {
        'total_products': total_products,
        'total_categories': total_categories,
        'total_sales': total_sales,
        'total_revenue': round(total_revenue, 2),

        'today_revenue': round(today_revenue, 2),
        'weekly_revenue': round(weekly_revenue, 2),
        'monthly_revenue': round(monthly_revenue, 2),

        'chart_labels': chart_labels,
        'chart_data': chart_data,
        'monthly_report': monthly_report,
    }

    return render(request, 'dashboard.html', context)


@login_required
def add_category(request):
    form = CategoryForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('dashboard')
    return render(request, 'form.html', {'form': form})


@login_required
def add_product(request):
    form = ProductForm(request.POST or None)
    if form.is_valid():
        product = form.save(commit=False)
        product.created_by = request.user
        product.save()
        return redirect('dashboard')
    return render(request, 'form.html', {'form': form})


@login_required
def add_sale(request):
    form = SaleForm(request.POST or None)
    if form.is_valid():
        sale = form.save()
        product = sale.product
        product.quantity -= sale.quantity_sold
        product.save()
        return redirect('dashboard')
    return render(request, 'form.html', {'form': form})