from django.urls import path

from .views import ClientCreateView, ClientDeleteView, ClientListView, ClientUpdateView

app_name = "clientes"

urlpatterns = [
    path("", ClientListView.as_view(), name="list"),
    path("nuevo/", ClientCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", ClientUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", ClientDeleteView.as_view(), name="delete"),
]
