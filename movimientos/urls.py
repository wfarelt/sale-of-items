from django.urls import path

from .views import InventoryMovementDetailView, InventoryMovementListView

app_name = "movimientos"

urlpatterns = [
	path("", InventoryMovementListView.as_view(), name="list"),
	path("<int:pk>/", InventoryMovementDetailView.as_view(), name="detail"),
]
