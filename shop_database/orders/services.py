from typing import Tuple

from django.db import transaction
from django.utils import timezone

from orders.exceptions import (
    InsufficientStockException,
    OrderNotModifiableException,
    ArticleNotFoundException,
    OrderNotFoundException
)
from orders.models import Article, Order, ItemInOrder


class OrderService:
    """Сервис для работы с заказами."""
    @transaction.atomic
    def add_item_to_order(
        self, order_id: int, article_id: int, quantity: int
    ) -> ItemInOrder:
        """
        Добавляет товар в заказ. Если товар уже есть в заказе – увеличивает
        количество.
        """
        order, article = self._get_order_and_article_for_new_item(
            order_id, article_id, quantity
        )
        item = self._create_or_update_item(order, article, quantity)
        self._update_order_time(order)
        return item

    @staticmethod
    def _get_order_and_article_for_new_item(
        order_id: int, article_id: int, quantity: int
    ) -> Tuple[Order, Article]:
        """Получает и проверяет доступность Order и Article для заказа."""
        try:
            order = Order.objects.select_for_update().get(id=order_id)
            if not order.is_modified():
                raise OrderNotModifiableException()
        except Order.DoesNotExist:
            raise OrderNotFoundException()
        try:
            article = Article.objects.select_for_update().get(id=article_id)
            if not article.is_available_quantity(quantity):
                raise InsufficientStockException(
                    detail=(f'Доступно не более {article.quantity} шт.')
                )
        except Article.DoesNotExist:
            raise ArticleNotFoundException()
        return order, article

    @staticmethod
    def _create_or_update_item(
        order: Order, article: Article, quantity: int
    ) -> ItemInOrder:
        try:
            item = ItemInOrder.objects.select_for_update().get(
                order=order, article=article
            )
            new_quantity = item.quantity + quantity
            if not article.is_available_quantity(new_quantity):
                raise InsufficientStockException(
                    detail=(
                        f'Доступно всего не более {article.quantity} шт. '
                        f'В заказе уже добавлено {item.quantity} шт.'
                    )
                )
            item.quantity = new_quantity
            item.save(update_fields=['quantity'])
        except ItemInOrder.DoesNotExist:
            item = ItemInOrder.objects.create(
                order=order,
                article=article,
                quantity=quantity,
                price_in_order=article.price
            )
        return item

    @staticmethod
    def _update_order_time(order: Order) -> None:
        order.updated_at = timezone.now()
        order.save(update_fields=['updated_at'])
