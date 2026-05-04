from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import CommercialCondition, PaymentMethod, Sale, SaleDetail


class SaleForm(forms.ModelForm):
	upfront_amount = forms.DecimalField(
		required=False,
		min_value=Decimal("0.01"),
		decimal_places=2,
		max_digits=12,
		label="Pago inicial",
		widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01", "placeholder": "0.00"}),
	)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["client"].queryset = self.fields["client"].queryset.filter(is_active=True)
		self.fields["commercial_condition"].queryset = CommercialCondition.objects.filter(is_active=True)
		self.fields["payment_type"].required = False
		self.fields["status"].choices = [
			(Sale.STATUS_PROFORMA, "Proforma"),
			(Sale.STATUS_CONFIRMED, "Confirmada"),
		]
		if not self.instance.pk:
			self.fields["status"].initial = Sale.STATUS_PROFORMA
			cash_condition = CommercialCondition.objects.filter(code=CommercialCondition.CODE_CASH, is_active=True).first()
			if cash_condition:
				self.fields["commercial_condition"].initial = cash_condition

	class Meta:
		model = Sale
		fields = ["client", "commercial_condition", "payment_type", "status"]
		widgets = {
			"client": forms.Select(attrs={"class": "form-select"}),
			"commercial_condition": forms.Select(attrs={"class": "form-select"}),
			"payment_type": forms.Select(attrs={"class": "form-select"}),
			"status": forms.Select(attrs={"class": "form-select"}),
		}

	def clean(self):
		cleaned_data = super().clean()
		status = cleaned_data.get("status")
		condition = cleaned_data.get("commercial_condition")
		payment_type = cleaned_data.get("payment_type")
		upfront_amount = cleaned_data.get("upfront_amount")

		if status == Sale.STATUS_CONFIRMED:
			if not condition:
				self.add_error("commercial_condition", "Selecciona una condición comercial.")
			elif condition.is_cash_sale:
				if not payment_type:
					self.add_error("payment_type", "Selecciona el método de pago para la venta al contado.")
				if upfront_amount is None:
					self.add_error("upfront_amount", "En contado debes registrar al menos un pago inicial.")

		if upfront_amount is not None and not payment_type:
			self.add_error("payment_type", "Selecciona método de pago para registrar el pago inicial.")

		return cleaned_data


class SalePaymentForm(forms.Form):
	method = forms.ModelChoiceField(
		queryset=PaymentMethod.objects.filter(is_active=True),
		label="Método de pago",
		widget=forms.Select(attrs={"class": "form-select"}),
	)
	amount = forms.DecimalField(
		min_value=Decimal("0.01"),
		max_digits=12,
		decimal_places=2,
		label="Monto",
		widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
	)
	reference = forms.CharField(
		required=False,
		max_length=80,
		label="Referencia",
		widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Nro. operación (opcional)"}),
	)
	notes = forms.CharField(
		required=False,
		max_length=255,
		label="Observación",
		widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "Detalle opcional"}),
	)


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

			if price is not None and discount is not None:
				max_discount = (quantity * price) * Decimal("0.20")
				if discount > max_discount:
					raise ValidationError(f"El descuento de {product.name} no puede superar el 20% del subtotal bruto.")

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
