from django.contrib import admin
from .models import Category, Product, Sale

# Optional: Customize admin display
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'quantity', 'created_by')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'quantity_sold', 'sale_date', 'total_price')
    list_filter = ('sale_date', 'product')
    search_fields = ('product__name',)

    # Show total price in admin
    def total_price(self, obj):
        return obj.quantity_sold * obj.product.price
    total_price.short_description = 'Total Price'

