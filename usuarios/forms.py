from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.cache import cache
from django.core.exceptions import ValidationError

from .security import build_login_lock_key, get_client_ip
from .models import Role, User


class LoginProtectionAuthenticationForm(AuthenticationForm):
	"""Authentication form with temporary lockout after repeated failures."""

	error_messages = {
		"invalid_login": "Usuario o contrasena incorrectos.",
		"inactive": "Esta cuenta esta inactiva.",
		"locked": "Demasiados intentos fallidos. Intenta nuevamente mas tarde.",
	}

	def clean(self):
		username = self.cleaned_data.get("username")
		password = self.cleaned_data.get("password")

		if username is None or password is None:
			return self.cleaned_data

		max_attempts = getattr(settings, "LOGIN_FAILURE_LIMIT", 5)
		lockout_seconds = getattr(settings, "LOGIN_LOCKOUT_SECONDS", 900)
		request = getattr(self, "request", None)
		client_ip = get_client_ip(request)
		lock_key = build_login_lock_key(username=username, ip_address=client_ip)

		failed_attempts = cache.get(lock_key, 0)
		if failed_attempts >= max_attempts:
			raise self.get_invalid_login_error(code="locked")

		self.user_cache = authenticate(
			self.request, username=username, password=password
		)
		if self.user_cache is None:
			failed_attempts += 1
			cache.set(lock_key, failed_attempts, timeout=lockout_seconds)
			if failed_attempts >= max_attempts:
				raise self.get_invalid_login_error(code="locked")
			raise self.get_invalid_login_error(code="invalid_login")

		cache.delete(lock_key)
		self.confirm_login_allowed(self.user_cache)
		return self.cleaned_data

	def get_invalid_login_error(self, code="invalid_login"):
		return ValidationError(
			self.error_messages[code],
			code=code,
		)


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
