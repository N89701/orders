from django.urls import path
from .views import AddToOrderView

urlpatterns = [
    path('add-to-order/', AddToOrderView.as_view(), name='add-to-order'),
]
