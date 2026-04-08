from django import forms

from django.utils import timezone

from .models import CashBox, CashBoxClosure


class CashBoxForm(forms.ModelForm):
	date = forms.DateTimeField(
		input_formats=["%Y-%m-%dT%H:%M"],
		widget=forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}, format="%Y-%m-%dT%H:%M"),
	)

	class Meta:
		model = CashBox
		fields = ["date", "type", "amount", "payment_method", "description", "reference"]
		widgets = {
			"type": forms.Select(attrs={"class": "form-select"}),
			"amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
			"payment_method": forms.Select(attrs={"class": "form-select"}),
			"description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
			"reference": forms.Select(attrs={"class": "form-select"}),
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		if self.instance and self.instance.pk and self.instance.date:
			self.initial["date"] = self.instance.date.strftime("%Y-%m-%dT%H:%M")
		elif not self.is_bound:
			self.initial["date"] = timezone.localtime().strftime("%Y-%m-%dT%H:%M")


class CashBoxOpeningForm(forms.Form):
	date = forms.DateField(
		input_formats=["%Y-%m-%d"],
		widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
	)
	opening_balance = forms.DecimalField(
		max_digits=12,
		decimal_places=2,
		min_value=0,
		widget=forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
		label="Saldo inicial",
	)


class CashBoxCloseForm(forms.Form):
	date = forms.DateField(
		input_formats=["%Y-%m-%d"],
		widget=forms.DateInput(attrs={"class": "form-control", "type": "date"}),
	)

	def get_summary(self):
		if not self.is_valid():
			return None
		return CashBoxClosure.get_day_summary(self.cleaned_data["date"])
