from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse_lazy

from .models import Role, User


class LoginView(SuccessMessageMixin, auth_views.LoginView):
    template_name = "usuarios/login.html"
    authentication_form = AuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = "usuarios:login"


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "usuarios/password_change.html"
    success_url = reverse_lazy("usuarios:password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "usuarios/password_change_done.html"


@login_required
def dashboard_view(request):
    user = request.user
    role = user.role.name

    context = {"page_title": "Dashboard"}

    if role == "admin":
        context.update(
            {
                "users_total": User.objects.count(),
                "users_active": User.objects.filter(is_active=True).count(),
                "users_inactive": User.objects.filter(is_active=False).count(),
                "roles_total": Role.objects.count(),
                "users_by_role": Role.objects.annotate(total=Count("user")),
            }
        )
    elif role == "vendedor":
        context.update(
            {
                "ventas_hoy": 0,
                "ventas_mes": 0,
                "clientes_total": 0,
            }
        )
    elif role == "almacen":
        context.update(
            {
                "productos_total": 0,
                "stock_bajo": 0,
                "entradas_hoy": 0,
            }
        )

    return render(request, "usuarios/dashboard.html", context)
