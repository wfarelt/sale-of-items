from django.urls import path

from .views import CashBoxCloseView, CashBoxCreateView, CashBoxDayReportPDFView, CashBoxDeleteView, CashBoxDetailView, CashBoxListView, CashBoxOpeningView

app_name = "caja"

urlpatterns = [
	path("", CashBoxListView.as_view(), name="list"),
	path("crear/", CashBoxCreateView.as_view(), name="create"),
	path("saldo-inicial/", CashBoxOpeningView.as_view(), name="opening"),
	path("cerrar-dia/", CashBoxCloseView.as_view(), name="close"),
	path("informe-pdf/", CashBoxDayReportPDFView.as_view(), name="report_pdf"),
	path("<int:pk>/", CashBoxDetailView.as_view(), name="detail"),
	path("<int:pk>/eliminar/", CashBoxDeleteView.as_view(), name="delete"),
]
