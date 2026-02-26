import django_filters

from .models import Category


class CategoryFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains', label='Category name')

    class Meta:
        model = Category
        fields = ['name']