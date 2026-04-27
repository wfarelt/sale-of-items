from django.urls import path
from .views import AlmacenListView, AlmacenCreateView, AlmacenUpdateView, AlmacenDisableView

app_name = "almacenes"

urlpatterns = [
    path("", AlmacenListView.as_view(), name="list"),
    path("nuevo/", AlmacenCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", AlmacenUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", AlmacenDisableView.as_view(), name="delete"),
]
