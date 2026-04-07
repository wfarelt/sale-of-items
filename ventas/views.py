from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from productos.models import Product
from .forms import SaleDetailFormSet, SaleForm
from .models import Sale


class SalesAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_vendedor


class SaleListView(SalesAccessMixin, ListView):
	model = Sale
	template_name = "ventas/sale_list.html"
	context_object_name = "sales"
	paginate_by = 20

	def get_queryset(self):
		queryset = Sale.objects.select_related("client")
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(client__name__icontains=search)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		return context


class SaleDetailView(SalesAccessMixin, DetailView):
	model = Sale
	template_name = "ventas/sale_detail.html"
	context_object_name = "sale"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["details"] = self.object.saledetail_set.select_related("product")
		return context


class SaleCreateView(SalesAccessMixin, CreateView):
	model = Sale
	form_class = SaleForm
	template_name = "ventas/sale_form.html"
	success_url = reverse_lazy("ventas:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		formset = SaleDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()
			try:
				self.object.apply_inventory_output()
			except ValidationError as exc:
				messages.error(request, str(exc))
				self.object.delete()
				return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

			messages.success(request, "Venta registrada exitosamente.")
			return redirect(self.success_url)

		return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = SaleDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = SaleDetailFormSet(instance=self.object)
		kwargs["products_data"] = list(Product.objects.values("id", "stock", "price"))
		return super().get_context_data(**kwargs)


class SaleDeleteView(SalesAccessMixin, DeleteView):
	model = Sale
	template_name = "ventas/sale_confirm_delete.html"
	success_url = reverse_lazy("ventas:list")

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		for detail in self.object.saledetail_set.select_related("product"):
			product = detail.product
			product.stock += detail.quantity
			product.save(update_fields=["stock"])
		messages.warning(request, "Venta eliminada y stock restaurado.")
		return super().post(request, *args, **kwargs)
