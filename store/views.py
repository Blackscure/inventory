from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, DecimalField, Sum, F,ExpressionWrapper
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

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'category_list.html', {'categories': categories})

def product_list(request):
    products = Product.objects.select_related('category').all()
    return render(request, 'product_list.html', {'products': products})

def sale_list(request):
    sales = Sale.objects.select_related('product').all()

    for sale in sales:
        sale.total_price = sale.quantity_sold * sale.product.price

    return render(request, 'sale_list.html', {'sales': sales})

def add_sale(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm()
    return render(request, 'sale_form.html', {'form': form, 'title': 'Record Sale'})

def edit_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            form.save()
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sale_form.html', {'form': form, 'title': 'Edit Sale'})

def delete_sale(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        sale.delete()
        return redirect('sale_list')
    return render(request, 'sale_confirm_delete.html', {'sale': sale})

def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm()
    return render(request, 'category_form.html', {'form': form, 'title': 'Add Category'})


def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect('category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'category_form.html', {'form': form, 'title': 'Edit Category'})


def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'product_form.html', {'form': form, 'title': 'Add Product'})

def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'product_form.html', {'form': form, 'title': 'Edit Product'})

def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        return redirect('product_list')
    return render(request, 'product_confirm_delete.html', {'product': product})


def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        category.delete()
        return redirect('category_list')
    return render(request, 'category_confirm_delete.html', {'category': category})


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

    # CATEGORY PIE CHART
    # -----------------------------
    category_data = (
        Category.objects
        .annotate(product_count=Count('product'))
    )

    pie_labels = []
    pie_data = []

    for category in category_data:
        pie_labels.append(category.name)
        pie_data.append(category.product_count)

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
        'pie_labels': pie_labels,
        'pie_data': pie_data,
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