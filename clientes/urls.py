from django.urls import path

from .views import (
    ClientCreateView,
    ClientDeleteView,
    ClientListView,
    ClientLookupView,
    ClientQuickCreateView,
    ClientUpdateView,
)
from .views import AccountStatementView, AccountStatementPdfView

app_name = "clientes"

urlpatterns = [
    path("", ClientListView.as_view(), name="list"),
    path("nuevo/", ClientCreateView.as_view(), name="create"),
    path("api/buscar/", ClientLookupView.as_view(), name="lookup"),
    path("api/crear-rapido/", ClientQuickCreateView.as_view(), name="quick_create"),
    path("<int:pk>/editar/", ClientUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", ClientDeleteView.as_view(), name="delete"),
    path("<int:pk>/estado-cuenta/", AccountStatementView.as_view(), name="account_statement"),
    path("<int:pk>/estado-cuenta/pdf/", AccountStatementPdfView.as_view(), name="account_statement_pdf"),
]
