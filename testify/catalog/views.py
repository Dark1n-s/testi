import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from .models import Product, Order, OrderItem

# 1. Віддаємо товари
def product_list_api(request):
    products = Product.objects.all()
    data = []
    for item in products:
        data.append({
            'id': item.id,
            'name': item.name,
            'price': float(item.price),
            'stock': item.stock,
            'is_in_stock': item.stock > 0 # Повертаємо True, якщо товар є
        })
    return JsonResponse(data, safe=False)

# 2. Оформлюємо замовлення
@csrf_exempt # Вимикаємо захист CSRF для спрощення тестування API
def create_order_api(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Метод не підтримується'}, status=405)

    try:
        # Читаємо JSON, який надіслав фронтенд
        payload = json.loads(request.body)
        customer_name = payload.get('customer_name')
        customer_phone = payload.get('customer_phone')
        cart_items = payload.get('items', []) # Це список куплених товарів

        # transaction.atomic() гарантує, що або все замовлення успішно запишеться, 
        # або, якщо станеться помилка (наприклад, не вистачить товару), база даних 
        # відкотить усі зміни назад. Це захист від "зламаних" замовлень.
        with transaction.atomic():
            total_sum = 0
            order_items_to_create = []

            for item_data in cart_items:
                product_id = item_data.get('product_id')
                quantity = int(item_data.get('quantity', 1))

                # select_for_update() блокує цей товар у базі на частку секунди.
                # Це потрібно, щоб два клієнти не купили останній товар одночасно.
                product = Product.objects.select_for_update().get(id=product_id)

                # Перевіряємо, чи є стільки товару на складі
                if product.stock < quantity:
                    return JsonResponse({'error': f'Мало товару: {product.name}'}, status=400)

                # Віднімаємо товар зі складу
                product.stock -= quantity
                product.save()

                item_total = product.price * quantity
                total_sum += item_total
                
                # Готуємо дані для створення рядка замовлення
                order_items_to_create.append({
                    'product': product,
                    'quantity': quantity,
                    'price': product.price
                })

            # Створюємо головне замовлення
            order = Order.objects.create(
                customer_name=customer_name,
                customer_phone=customer_phone,
                total_price=total_sum
            )

            # Записуємо всі товари в це замовлення
            for item in order_items_to_create:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )

        return JsonResponse({'success': True, 'order_id': order.id})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)