from django import forms
from django.forms import inlineformset_factory

from .models import Purchase, PurchaseDetail
from proveedores.models import Proveedor


class PurchaseForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["supplier"].queryset = Proveedor.objects.filter(activo=True).order_by("nombre")
		self.fields["supplier"].empty_label = "Selecciona un proveedor"
		self.fields["supplier"].required = True
		self.fields["invoice_number"].required = True
		if not self.fields["supplier"].queryset.exists():
			self.fields["supplier"].help_text = "No hay proveedores activos. Registra uno en el modulo de Proveedores."

	class Meta:
		model = Purchase
		fields = ["supplier", "invoice_number", "status"]
		widgets = {
			"supplier": forms.Select(attrs={"class": "form-select"}),
			"invoice_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Ej: F-000123"}),
			"status": forms.Select(attrs={"class": "form-select"}),
		}


class PurchaseDetailForm(forms.ModelForm):
	class Meta:
		model = PurchaseDetail
		fields = ["product", "quantity", "cost_price", "sale_price"]
		widgets = {
			"product": forms.Select(attrs={"class": "form-select"}),
			"quantity": forms.NumberInput(attrs={"class": "form-control", "min": "0.01", "step": "0.01"}),
			"cost_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
			"sale_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
		}


# Formset para manejar múltiples detalles de compra
PurchaseDetailFormSet = inlineformset_factory(
	Purchase,
	PurchaseDetail,
	form=PurchaseDetailForm,
	extra=1,
	can_delete=True,
	min_num=1,
	validate_min=True,
)
