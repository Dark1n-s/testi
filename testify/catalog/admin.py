from django.contrib import admin
from .models import Product, Order, OrderItem

# Цей клас каже: "покажи OrderItem всередині іншої сторінки"
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0 # Не показувати порожні зайві рядки

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'customer_phone', 'total_price', 'created_at')
    inlines = [OrderItemInline] # Підключаємо товари до сторінки замовлення

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')

admin.site.register(Product, ProductAdmin)
admin.site.register(Order, OrderAdmin)