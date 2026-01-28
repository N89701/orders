from rest_framework import serializers

from orders.models import ItemInOrder
from orders.services import OrderService


class ItemAddingSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(min_value=1)
    article_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)

    def create(self, validated_data):
        """Добавление товара в заказ"""
        creation_data = {
            key: validated_data[key]
            for key in ('order_id', 'article_id', 'quantity')
        }
        return OrderService().add_item_to_order(**creation_data)

    def to_representation(self, instance):
        serializer = ItemInOrderSerializer(instance)
        return serializer.data


class ItemInOrderSerializer(serializers.ModelSerializer):
    article = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = ItemInOrder
        fields = (
            'id',
            'article',
            'order',
            'price_in_order',
            'quantity',
            'total_price'
        )
