from django import forms
from django.forms import inlineformset_factory

from .models import Purchase, PurchaseDetail


class PurchaseForm(forms.ModelForm):
	class Meta:
		model = Purchase
		fields = ["supplier", "status"]
		widgets = {
			"supplier": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre del proveedor"}),
			"status": forms.Select(attrs={"class": "form-select"}),
		}


class PurchaseDetailForm(forms.ModelForm):
	class Meta:
		model = PurchaseDetail
		fields = ["product", "quantity", "cost_price", "sale_price"]
		widgets = {
			"product": forms.Select(attrs={"class": "form-select"}),
			"quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
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
