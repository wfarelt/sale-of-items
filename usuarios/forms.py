from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Role, User


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


class BaseCompanyUserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = [
			"first_name",
			"last_name",
			"username",
			"email",
			"phone",
			"address",
			"role",
			"is_active",
		]
		widgets = {
			"first_name": forms.TextInput(attrs={"class": "form-control"}),
			"last_name": forms.TextInput(attrs={"class": "form-control"}),
			"username": forms.TextInput(attrs={"class": "form-control"}),
			"email": forms.EmailInput(attrs={"class": "form-control"}),
			"phone": forms.TextInput(attrs={"class": "form-control"}),
			"address": forms.TextInput(attrs={"class": "form-control"}),
			"role": forms.Select(attrs={"class": "form-select"}),
			"is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
		}
		labels = {
			"first_name": "Nombre",
			"last_name": "Apellido",
			"username": "Nombre de usuario",
			"email": "Correo",
			"phone": "Telefono",
			"address": "Direccion",
			"role": "Rol",
			"is_active": "Activo",
		}

	def __init__(self, *args, **kwargs):
		self.company = kwargs.pop("company", None)
		super().__init__(*args, **kwargs)
		self.fields["email"].required = False
		self.fields["phone"].required = False
		self.fields["address"].required = False
		self.fields["role"].queryset = Role.objects.filter(name__in=["admin", "vendedor", "almacen"]).order_by("name")

	def clean_role(self):
		role = self.cleaned_data["role"]
		if role.name not in {"admin", "vendedor", "almacen"}:
			raise ValidationError("No puedes asignar ese rol.")
		return role

	def save(self, commit=True):
		user = super().save(commit=False)
		if self.company:
			user.company = self.company
		if commit:
			user.save()
		return user


class CompanyUserCreateForm(BaseCompanyUserForm):
	password1 = forms.CharField(
		label="Contrasena",
		widget=forms.PasswordInput(attrs={"class": "form-control"}),
	)
	password2 = forms.CharField(
		label="Confirmar contrasena",
		widget=forms.PasswordInput(attrs={"class": "form-control"}),
	)

	def clean(self):
		cleaned_data = super().clean()
		password1 = cleaned_data.get("password1")
		password2 = cleaned_data.get("password2")

		if password1 and password2 and password1 != password2:
			self.add_error("password2", "Las contrasenas no coinciden.")

		if password1:
			try:
				validate_password(password1, user=self.instance)
			except ValidationError as exc:
				self.add_error("password1", exc)

		return cleaned_data

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user


class CompanyUserUpdateForm(BaseCompanyUserForm):
	pass
