from rest_framework import serializers

from orders.models import Article, ArticleInOrder, Order


class ArticleAddingSerializer(serializers.Serializer):
    order_id = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all())
    article_id = serializers.PrimaryKeyRelatedField(
        queryset=Article.objects.all()
    )
    quantity = serializers.IntegerField()


class ArticleInOrderSerializer(serializers.ModelSerializer):
    article = serializers.CharField(source='article.title', read_only=True)

    class Meta:
        model = ArticleInOrder
        fields = (
            'id',
            'article',
            'order', 
            'price_in_order',
            'quantity',
            'total_price'
        )
