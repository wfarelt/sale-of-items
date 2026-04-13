from django.urls import path

from .views import CompanySettingsUpdateView

app_name = "empresas"

urlpatterns = [
	path("configuracion/", CompanySettingsUpdateView.as_view(), name="settings"),
]
