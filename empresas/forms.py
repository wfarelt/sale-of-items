from django import forms

from .models import Company


class CompanySettingsForm(forms.ModelForm):
	class Meta:
		model = Company
		fields = [
			"name",
			"ruc_nit",
			"email",
			"phone",
			"address",
			"city",
			"country",
			"currency",
			"timezone",
			"logo",
		]
		widgets = {
			"name": forms.TextInput(attrs={"class": "form-control"}),
			"ruc_nit": forms.TextInput(attrs={"class": "form-control"}),
			"email": forms.EmailInput(attrs={"class": "form-control"}),
			"phone": forms.TextInput(attrs={"class": "form-control"}),
			"address": forms.TextInput(attrs={"class": "form-control"}),
			"city": forms.TextInput(attrs={"class": "form-control"}),
			"country": forms.TextInput(attrs={"class": "form-control"}),
			"currency": forms.TextInput(attrs={"class": "form-control", "maxlength": "10"}),
			"timezone": forms.TextInput(attrs={"class": "form-control"}),
			"logo": forms.ClearableFileInput(attrs={"class": "form-control"}),
		}
