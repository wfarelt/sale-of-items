from django import forms

from .models import User


class ProfileForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ["first_name", "last_name", "username", "email", "phone", "address"]
		widgets = {
			"first_name": forms.TextInput(attrs={"class": "form-control"}),
			"last_name": forms.TextInput(attrs={"class": "form-control"}),
			"username": forms.TextInput(attrs={"class": "form-control"}),
			"email": forms.EmailInput(attrs={"class": "form-control"}),
			"phone": forms.TextInput(attrs={"class": "form-control"}),
			"address": forms.TextInput(attrs={"class": "form-control"}),
		}
		labels = {
			"first_name": "Nombre",
			"last_name": "Apellido",
			"username": "Nombre de usuario",
			"email": "Correo electrónico",
			"phone": "Teléfono",
			"address": "Dirección",
		}

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields["email"].required = False
		self.fields["phone"].required = False
		self.fields["address"].required = False
