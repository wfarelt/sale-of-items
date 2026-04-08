from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Sale, SaleDetail


class SaleForm(forms.ModelForm):
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
		fields = ["product", "quantity", "price"]
		widgets = {
			"product": forms.Select(attrs={"class": "form-select"}),
			"quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
			"price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
		}


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
			if not product or not quantity:
				continue

			if product.pk in products_qty:
				raise ValidationError("No puedes repetir el mismo producto en una venta.")

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
