from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from clientes.models import Client
from caja.models import CashBox
from movimientos.models import InventoryMovement
from productos.models import Product
from compras.models import Purchase
from ventas.models import Sale
from .forms import ProfileForm
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

	context = {"page_title": "Dashboard"}

	if user.is_superuser:
		context.update(
			{
				"page_title": "Panel de administracion",
				"admin_panel_url": "/admin/",
				"users_total": User.objects.count(),
				"users_active": User.objects.filter(is_active=True).count(),
				"users_inactive": User.objects.filter(is_active=False).count(),
				"roles_total": Role.objects.count(),
				"users_by_role": Role.objects.annotate(total=Count("user")),
			}
		)
	elif user.is_admin:
		now = timezone.localtime()
		month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		context.update(
			{
				"clients_total": Client.objects.count(),
				"products_total": Product.objects.count(),
				"products_low_stock": Product.objects.filter(stock__lte=5).count(),
				"purchases_total": Purchase.objects.count(),
				"purchases_pending": Purchase.objects.filter(status="pendiente").count(),
				"purchases_total_value": Purchase.objects.filter(status="recibida").aggregate(Sum("total"))["total__sum"] or 0,
				"sales_total": Sale.objects.count(),
				"sales_today_total": Sale.objects.filter(date__date=now.date()).count(),
				"sales_today_amount": Sale.objects.filter(date__date=now.date()).aggregate(Sum("total"))["total__sum"] or 0,
				"sales_month_total": Sale.objects.filter(date__gte=month_start).aggregate(Sum("total"))["total__sum"] or 0,
				"movements_total": InventoryMovement.objects.count(),
				"cash_entries_total": CashBox.objects.count(),
				"cash_income_month": CashBox.objects.filter(type=CashBox.TYPE_INCOME, date__gte=month_start).aggregate(Sum("amount"))["amount__sum"] or 0,
				"cash_expense_month": CashBox.objects.filter(type=CashBox.TYPE_EXPENSE, date__gte=month_start).aggregate(Sum("amount"))["amount__sum"] or 0,
			}
		)
		context["cash_balance_month"] = context["cash_income_month"] - context["cash_expense_month"]
	elif user.is_vendedor:
		now = timezone.localtime()
		month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		context.update(
			{
				"ventas_hoy": Sale.objects.filter(date__date=now.date()).count(),
				"ventas_mes": Sale.objects.filter(date__gte=month_start).count(),
				"caja_mes": CashBox.objects.filter(date__gte=month_start, type=CashBox.TYPE_INCOME).aggregate(Sum("amount"))["amount__sum"] or 0,
				"ultimas_ventas": Sale.objects.select_related("client").all()[:5],
				"clientes_total": Client.objects.count(),
			}
		)
	elif user.is_almacen:
		now = timezone.localtime()
		context.update(
			{
				"productos_total": Product.objects.count(),
				"stock_bajo": Product.objects.filter(stock__lte=5).count(),
				"purchases_total": Purchase.objects.count(),
				"purchases_pending": Purchase.objects.filter(status="pendiente").count(),
				"movements_total": InventoryMovement.objects.count(),
				"entradas_hoy": InventoryMovement.objects.filter(type="IN", date__date=now.date()).count(),
			}
		)

	return render(request, "usuarios/dashboard.html", context)


@login_required
def profile_view(request):
	if request.method == "POST":
		form = ProfileForm(request.POST, instance=request.user)
		if form.is_valid():
			form.save()
			messages.success(request, "Perfil actualizado exitosamente.")
			return redirect("usuarios:profile")
	else:
		form = ProfileForm(instance=request.user)
	return render(request, "usuarios/profile.html", {"form": form})
