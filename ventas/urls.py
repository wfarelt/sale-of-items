from django.urls import path

from .views import SaleCreateView, SaleDeleteView, SaleDetailView, SaleListView, SaleUpdateView

app_name = "ventas"

urlpatterns = [
	path("", SaleListView.as_view(), name="list"),
	path("crear/", SaleCreateView.as_view(), name="create"),
	path("<int:pk>/", SaleDetailView.as_view(), name="detail"),
	path("<int:pk>/editar/", SaleUpdateView.as_view(), name="update"),
	path("<int:pk>/eliminar/", SaleDeleteView.as_view(), name="delete"),
]
