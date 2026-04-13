from django.urls import path

from .views import InventoryMovementDetailView, InventoryMovementListView, InventoryMovementPDFView

app_name = "movimientos"

urlpatterns = [
	path("", InventoryMovementListView.as_view(), name="list"),
	path("<int:pk>/", InventoryMovementDetailView.as_view(), name="detail"),
	path("<int:pk>/pdf/", InventoryMovementPDFView.as_view(), name="pdf"),
]
