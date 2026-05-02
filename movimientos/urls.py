from django.urls import path

from .views import (
	InventoryMovementDetailView,
	InventoryMovementListView,
	InventoryMovementManualCreateView,
	InventoryMovementPDFView,
)

app_name = "movimientos"

urlpatterns = [
	path("", InventoryMovementListView.as_view(), name="list"),
	path("manual/crear/", InventoryMovementManualCreateView.as_view(), name="manual_create"),
	path("<int:pk>/", InventoryMovementDetailView.as_view(), name="detail"),
	path("<int:pk>/pdf/", InventoryMovementPDFView.as_view(), name="pdf"),
]
