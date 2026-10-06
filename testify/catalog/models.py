from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True) # blank=True означає, що опис необов'язковий
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0) # PositiveIntegerField не дозволяє кількості бути менше нуля

    def __str__(self):
        return f"{self.name} ({self.stock} шт.)"

class Order(models.Model):
    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True) # Автоматично запише час створення

    def __str__(self):
        return f"Замовлення #{self.id} — {self.customer_name}"

class OrderItem(models.Model):
    # ForeignKey створює зв'язок. Якщо видалити замовлення (CASCADE), видаляться і його рядки.
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    # PROTECT забороняє видаляти товар з бази, якщо він вже є в чиємусь замовленні.
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Фіксуємо ціну на момент покупки