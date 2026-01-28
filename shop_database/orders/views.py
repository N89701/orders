from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.serializers import ItemAddingSerializer
from orders.exceptions import (
    ArticleNotFoundException,
    InsufficientStockException,
    OrderNotModifiableException,
    OrderNotFoundException,
)


class AddToOrderView(APIView):
    def post(self, request):
        serializer = ItemAddingSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            except (
                OrderNotFoundException,
                ArticleNotFoundException,
                OrderNotModifiableException,
                InsufficientStockException
            ) as e:
                return Response({'error': e.detail}, status=e.status_code)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
