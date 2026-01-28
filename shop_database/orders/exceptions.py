from rest_framework.exceptions import APIException
from rest_framework import status


class InsufficientStockException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Недостаточно товара на складе'
    default_code = 'insufficient_stock'


class OrderNotModifiableException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Заказ нельзя изменить'
    default_code = 'order_not_modifiable'


class ArticleNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Товар не найден'
    default_code = 'article_not_found'


class OrderNotFoundException(APIException):
    status_code = status.HTTP_404_NOT_FOUND
    default_detail = 'Заказ не найден'
    default_code = 'order_not_found'
