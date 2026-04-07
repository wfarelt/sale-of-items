from django.urls import path

from .views import (
	PurchaseListView,
	PurchaseDetailView,
	PurchaseCreateView,
	PurchaseUpdateView,
	PurchaseDeleteView,
)

app_name = "compras"

urlpatterns = [
	path("", PurchaseListView.as_view(), name="list"),
	path("<int:pk>/", PurchaseDetailView.as_view(), name="detail"),
	path("crear/", PurchaseCreateView.as_view(), name="create"),
	path("<int:pk>/editar/", PurchaseUpdateView.as_view(), name="update"),
	path("<int:pk>/eliminar/", PurchaseDeleteView.as_view(), name="delete"),
]
