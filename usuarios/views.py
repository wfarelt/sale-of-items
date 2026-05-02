from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Q, Sum
from django.db.models.functions import TruncDate
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from clientes.models import Client
from caja.models import CashBox
from movimientos.models import InventoryMovement
from productos.models import Product
from compras.models import Purchase
from ventas.models import Sale
from .forms import CompanyUserCreateForm, CompanyUserUpdateForm, LoginProtectionAuthenticationForm, ProfileForm
from .models import Role, User


class LoginView(SuccessMessageMixin, auth_views.LoginView):
    template_name = "usuarios/login.html"
    authentication_form = LoginProtectionAuthenticationForm
    redirect_authenticated_user = True


class LogoutView(auth_views.LogoutView):
    next_page = "usuarios:login"


class PasswordChangeView(auth_views.PasswordChangeView):
    template_name = "usuarios/password_change.html"
    success_url = reverse_lazy("usuarios:password_change_done")


class PasswordChangeDoneView(auth_views.PasswordChangeDoneView):
    template_name = "usuarios/password_change_done.html"


class CompanyUsersAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin


class CompanyUserListView(CompanyUsersAccessMixin, ListView):
	model = User
	template_name = "usuarios/user_list.html"
	context_object_name = "users"
	paginate_by = 10

	def get_queryset(self):
		queryset = (
			User.objects.select_related("role")
			.filter(is_superuser=False)
			.order_by("first_name", "last_name", "username")
		)
		search = self.request.GET.get("q", "").strip()
		if search:
			queryset = queryset.filter(
				Q(username__icontains=search)
				| Q(first_name__icontains=search)
				| Q(last_name__icontains=search)
				| Q(email__icontains=search)
			)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "").strip()
		return context


class CompanyUserCreateView(CompanyUsersAccessMixin, CreateView):
	model = User
	form_class = CompanyUserCreateForm
	template_name = "usuarios/user_form.html"
	success_url = reverse_lazy("usuarios:user_list")

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, "Usuario creado exitosamente.")
		return response


class CompanyUserUpdateView(CompanyUsersAccessMixin, UpdateView):
	model = User
	form_class = CompanyUserUpdateForm
	template_name = "usuarios/user_form.html"
	success_url = reverse_lazy("usuarios:user_list")

	def get_queryset(self):
		return User.objects.select_related("role").filter(is_superuser=False)

	def form_valid(self, form):
		response = super().form_valid(form)
		messages.success(self.request, "Usuario actualizado exitosamente.")
		return response


class CompanyUserDeleteView(CompanyUsersAccessMixin, DeleteView):
	model = User
	template_name = "usuarios/user_confirm_delete.html"
	success_url = reverse_lazy("usuarios:user_list")

	def get_queryset(self):
		return User.objects.select_related("role").filter(is_superuser=False)

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.pk == request.user.pk:
			messages.error(request, "No puedes cambiar tu propio estado desde este modulo.")
			return redirect(self.success_url)
		self.object.is_active = not self.object.is_active
		self.object.save(update_fields=["is_active", "updated_at"])
		if self.object.is_active:
			messages.success(request, "Usuario activado correctamente.")
		else:
			messages.warning(request, "Usuario desactivado correctamente.")
		return redirect(self.success_url)


@login_required
def dashboard_view(request):
	user = request.user

	context = {"page_title": "Dashboard"}

	if user.is_superuser:
		now = timezone.localtime()
		month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
		context.update(
			{
				"page_title": "Panel de administracion",
				"admin_panel_url": "/admin/",
				"users_total": User.objects.count(),
				"users_active": User.objects.filter(is_active=True).count(),
				"users_inactive": User.objects.filter(is_active=False).count(),
				"roles_total": Role.objects.count(),
				"clients_total": Client.objects.count(),
				"products_total": Product.objects.count(),
				"sales_month_total": Sale.objects.filter(date__gte=month_start).aggregate(Sum("total"))["total__sum"] or 0,
			}
		)
	elif user.is_admin:
		now = timezone.localtime()
		week_start_date = now.date() - timedelta(days=6)
		sales_last_week_qs = (
			Sale.objects.filter(
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
				"ventas_hoy": Sale.objects.filter(seller=user, date__date=now.date()).count(),
				"ventas_mes": Sale.objects.filter(seller=user, date__gte=month_start).count(),
				"ingresos_hoy": Sale.objects.filter(seller=user, status=Sale.STATUS_CONFIRMED, date__date=now.date()).aggregate(Sum("total"))["total__sum"] or 0,
				"caja_mes": CashBox.objects.filter(date__gte=month_start, type=CashBox.TYPE_INCOME, reference=CashBox.REFERENCE_SALE).aggregate(Sum("amount"))["amount__sum"] or 0,
				"ultimas_ventas": Sale.objects.filter(seller=user).select_related("client").all()[:5],
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
