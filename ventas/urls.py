from django.urls import path

from .views import (
	SaleAgingReportView,
	SaleCreateView,
	SaleCreatePurchaseView,
	SaleDeleteView,
	SaleDeliveryView,
	SaleDetailView,
	SaleListView,
	SaleDeliveryPDFView,
	SalePDFView,
	SaleSalePDFView,
	SaleRegisterPaymentView,
	SaleStatusTransitionView,
	SaleUpdateView,
)

app_name = "ventas"

urlpatterns = [
	path("", SaleListView.as_view(), name="list"),
	path("aging/", SaleAgingReportView.as_view(), name="aging_report"),
	path("crear/", SaleCreateView.as_view(), name="create"),
	path("<int:pk>/", SaleDetailView.as_view(), name="detail"),
	path("<int:pk>/editar/", SaleUpdateView.as_view(), name="update"),
	path("<int:pk>/entrega/", SaleDeliveryView.as_view(), name="delivery"),
	path("<int:pk>/registrar-pago/", SaleRegisterPaymentView.as_view(), name="register_payment"),
	path("<int:pk>/transicion/", SaleStatusTransitionView.as_view(), name="status_transition"),
	path("<int:pk>/crear-compra/", SaleCreatePurchaseView.as_view(), name="create_purchase"),
	path("<int:pk>/eliminar/", SaleDeleteView.as_view(), name="delete"),
	path("<int:pk>/pdf/venta/", SaleSalePDFView.as_view(), name="pdf_venta"),
	path("<int:pk>/pdf/entrega/", SaleDeliveryPDFView.as_view(), name="pdf_entrega"),
	path("<int:pk>/pdf/", SalePDFView.as_view(), name="pdf"),
]
