from django.urls import path
from .views import (
    ProveedorListView,
    ProveedorCreateView,
    ProveedorUpdateView,
    ProveedorDisableView,
)

app_name = "proveedores"

urlpatterns = [
    path("", ProveedorListView.as_view(), name="list"),
    path("nuevo/", ProveedorCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", ProveedorUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", ProveedorDisableView.as_view(), name="delete"),
]
