from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Sale, SaleDetail


class SaleForm(forms.ModelForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["client"].queryset = self.fields["client"].queryset.filter(is_active=True)
		self.fields["status"].choices = [
			(Sale.STATUS_PROFORMA, "Proforma"),
			(Sale.STATUS_CONFIRMED, "Confirmada"),
		]
		if not self.instance.pk:
			self.fields["status"].initial = Sale.STATUS_PROFORMA

	class Meta:
		model = Sale
		fields = ["client", "payment_type", "status"]
		widgets = {
			"client": forms.Select(attrs={"class": "form-select"}),
			"payment_type": forms.Select(attrs={"class": "form-select"}),
			"status": forms.Select(attrs={"class": "form-select"}),
		}


class SaleDetailForm(forms.ModelForm):
	class Meta:
		model = SaleDetail
		fields = ["product", "quantity", "price", "discount", "ref_m2", "cajas"]
		widgets = {
			"product": forms.Select(attrs={"class": "form-select"}),
			"quantity": forms.NumberInput(attrs={"class": "form-control", "min": "0.01", "step": "0.01"}),
			"price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
			"discount": forms.NumberInput(attrs={"class": "form-control", "min": "0", "step": "0.01"}),
			"ref_m2": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
			"cajas": forms.NumberInput(attrs={"class": "form-control", "min": "0"}),
		}


class SaleDeliveryForm(forms.ModelForm):
	class Meta:
		model = Sale
		fields = ["received_by_name", "received_by_doc", "delivery_notes"]
		widgets = {
			"received_by_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nombre completo de quien recoge"}),
			"received_by_doc": forms.TextInput(attrs={"class": "form-control", "placeholder": "CI / NIT / Documento"}),
			"delivery_notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Observaciones (opcional)"}),
		}

	def clean_received_by_name(self):
		value = (self.cleaned_data.get("received_by_name") or "").strip()
		if not value:
			raise ValidationError("El nombre de quien recoge es obligatorio.")
		return value

	def clean_received_by_doc(self):
		value = (self.cleaned_data.get("received_by_doc") or "").strip()
		if not value:
			raise ValidationError("El documento de quien recoge es obligatorio.")
		return value


class BaseSaleDetailFormSet(BaseInlineFormSet):
	def clean(self):
		super().clean()
		products_qty = {}

		for form in self.forms:
			if not hasattr(form, "cleaned_data"):
				continue
			if form.cleaned_data.get("DELETE"):
				continue

			product = form.cleaned_data.get("product")
			quantity = form.cleaned_data.get("quantity")
			price = form.cleaned_data.get("price")
			discount = form.cleaned_data.get("discount")
			if not product or not quantity:
				continue

			if product.pk in products_qty:
				raise ValidationError("No puedes repetir el mismo producto en una venta.")

			if price is not None and discount is not None and discount > (quantity * price):
				raise ValidationError(f"El descuento de {product.name} no puede ser mayor al subtotal bruto.")

			products_qty[product.pk] = quantity


SaleDetailFormSet = inlineformset_factory(
	Sale,
	SaleDetail,
	form=SaleDetailForm,
	formset=BaseSaleDetailFormSet,
	extra=1,
	can_delete=True,
	min_num=1,
	validate_min=True,
)
