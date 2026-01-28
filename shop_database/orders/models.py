from typing import Optional

from django.db import models


class Category(models.Model):
    title = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self', related_name='children', on_delete=models.CASCADE, null=True
    )
    position = models.PositiveSmallIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(parent=models.F('id')),
                name='self_parent_constraint'
            ),
            models.UniqueConstraint(
                fields=('parent', 'position'), name='unique_position_check'
            )
        ]


class Article(models.Model):
    title = models.CharField(max_length=100, db_index=True)
    description = models.TextField()
    category = models.ForeignKey(
        Category, related_name='articles', on_delete=models.CASCADE
    )
    price = models.DecimalField(max_digits=9, decimal_places=2, db_index=True)
    quantity = models.PositiveIntegerField()

    class Meta:
        constraints = (
            models.CheckConstraint(
                condition=models.Q(price__gt=0), name='positive_article_price'
            ),
        )

    def is_available_quantity(
        self, required_quantity: Optional[int] = 1
    ) -> bool:
        """Проверка доступности товара в заданном количестве."""
        return self.quantity >= required_quantity


class Client(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        CREATED = 'created'
        CANCELED = 'canceled'
        PAID = 'paid'
        DONE = 'done'
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    client = models.ForeignKey(
        Client, related_name='orders', on_delete=models.PROTECT
    )
    status = models.CharField(
        max_length=10, choices=StatusChoice.choices, default=StatusChoice.CREATED
    )

    @property
    def total_price(self):
        return self.articles.aggregate(
            total=models.Sum(models.F('quantity') * models.F('price_in_order'))
        )['total'] or 0

    def is_modified(self) -> bool:
        """Можно ли изменять заказ."""
        return self.status in (self.StatusChoice.CREATED,)


class ItemInOrder(models.Model):
    order = models.ForeignKey(
        Order, related_name='articles', on_delete=models.PROTECT, db_index=True
    )
    article = models.ForeignKey(
        Article, related_name='orders', on_delete=models.PROTECT
    )
    price_in_order = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()

    @property
    def total_price(self):
        return self.quantity * self.price_in_order

    def save(self, *args, **kwargs):
        if not self.pk:
            self.price_in_order = self.article.price
        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(price_in_order__gt=0),
                name='positive_item_price'
            ),
            models.CheckConstraint(
                condition=models.Q(quantity__gt=0), name='positive_quantity'
            ),
            models.UniqueConstraint(
                fields=('order', 'article'), name='unique_item'
            )
        ]
