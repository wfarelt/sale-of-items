from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone

from empresas.models import Company
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
	company = request.company

	context = {"page_title": "Dashboard"}

	if user.is_superuser:
		context.update(
			{
				"page_title": "Panel de administracion",
				"admin_panel_url": "/admin/",
				"companies_total": Company.objects.count(),
				"companies_active": Company.objects.filter(is_active=True).count(),
				"companies_inactive": Company.objects.filter(is_active=False).count(),
				"users_total": User.objects.count(),
				"users_with_company": User.objects.filter(company__isnull=False).count(),
				"users_without_company": User.objects.filter(company__isnull=True).count(),
				"users_active": User.objects.filter(is_active=True).count(),
				"users_inactive": User.objects.filter(is_active=False).count(),
				"roles_total": Role.objects.count(),
				"users_by_role": Role.objects.annotate(total=Count("user")),
				"companies_overview": Company.objects.annotate(
					users_count=Count("users", distinct=True),
				).order_by("-users_count", "name")[:10],
			}
		)
	elif user.is_admin:
		now = timezone.localtime()
		week_start_date = now.date() - timedelta(days=6)
		sales_last_week_qs = (
			Sale.objects.filter(
				company=company,
				status=Sale.STATUS_CONFIRMED,
				date__date__gte=week_start_date,
			)
			.annotate(day=TruncDate("date"))
			.values("day")
			.annotate(total=Sum("total"))
		)
		sales_by_day = {
			entry["day"]: float(entry["total"] or 0)
			for entry in sales_last_week_qs
		}
		weekly_labels = []
		weekly_amounts = []
		for offset in range(7):
			day = week_start_date + timedelta(days=offset)
			weekly_labels.append(day.strftime("%a %d/%m"))
			weekly_amounts.append(round(sales_by_day.get(day, 0), 2))

		month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		context.update(
			{
				"clients_total": Client.objects.filter(company=company).count(),
				"products_total": Product.objects.filter(company=company).count(),
				"products_low_stock": Product.objects.filter(company=company, stock__lte=5).count(),
				"purchases_total": Purchase.objects.filter(company=company).count(),
				"purchases_pending": Purchase.objects.filter(company=company, status="pendiente").count(),
				"purchases_total_value": Purchase.objects.filter(company=company, status="recibida").aggregate(Sum("total"))["total__sum"] or 0,
				"sales_total": Sale.objects.filter(company=company).count(),
				"sales_today_total": Sale.objects.filter(company=company, date__date=now.date()).count(),
				"sales_today_amount": Sale.objects.filter(company=company, date__date=now.date()).aggregate(Sum("total"))["total__sum"] or 0,
				"sales_month_total": Sale.objects.filter(company=company, date__gte=month_start).aggregate(Sum("total"))["total__sum"] or 0,
				"movements_total": InventoryMovement.objects.filter(company=company).count(),
				"cash_entries_total": CashBox.objects.filter(company=company).count(),
				"cash_income_month": CashBox.objects.filter(company=company, type=CashBox.TYPE_INCOME, date__gte=month_start).aggregate(Sum("amount"))["amount__sum"] or 0,
				"cash_expense_month": CashBox.objects.filter(company=company, type=CashBox.TYPE_EXPENSE, date__gte=month_start).aggregate(Sum("amount"))["amount__sum"] or 0,
				"weekly_sales_labels": weekly_labels,
				"weekly_sales_amounts": weekly_amounts,
			}
		)
		context["cash_balance_month"] = context["cash_income_month"] - context["cash_expense_month"]
	elif user.is_vendedor:
		now = timezone.localtime()
		month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		context.update(
			{
				"ventas_hoy": Sale.objects.filter(company=company, date__date=now.date()).count(),
				"ventas_mes": Sale.objects.filter(company=company, date__gte=month_start).count(),
				"caja_mes": CashBox.objects.filter(company=company, date__gte=month_start, type=CashBox.TYPE_INCOME).aggregate(Sum("amount"))["amount__sum"] or 0,
				"ultimas_ventas": Sale.objects.filter(company=company).select_related("client").all()[:5],
				"clientes_total": Client.objects.filter(company=company).count(),
			}
		)
	elif user.is_almacen:
		now = timezone.localtime()
		context.update(
			{
				"productos_total": Product.objects.filter(company=company).count(),
				"stock_bajo": Product.objects.filter(company=company, stock__lte=5).count(),
				"purchases_total": Purchase.objects.filter(company=company).count(),
				"purchases_pending": Purchase.objects.filter(company=company, status="pendiente").count(),
				"movements_total": InventoryMovement.objects.filter(company=company).count(),
				"entradas_hoy": InventoryMovement.objects.filter(company=company, type="IN", date__date=now.date()).count(),
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
