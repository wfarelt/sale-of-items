from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView, View

from config.pdf_utils import render_to_pdf
from empresas.mixins import CompanyQuerysetMixin
from productos.models import Product
from .forms import SaleDetailFormSet, SaleForm
from .models import Sale


class SalesAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_vendedor


class SaleListView(SalesAccessMixin, CompanyQuerysetMixin, ListView):
	model = Sale
	template_name = "ventas/sale_list.html"
	context_object_name = "sales"
	paginate_by = 20

	def get_queryset(self):
		queryset = super().get_queryset().select_related("client")
		search = self.request.GET.get("q")
		if search:
			queryset = queryset.filter(client__name__icontains=search)
		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		return context


class SaleDetailView(SalesAccessMixin, CompanyQuerysetMixin, DetailView):
	model = Sale
	template_name = "ventas/sale_detail.html"
	context_object_name = "sale"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["details"] = self.object.saledetail_set.select_related("product")
		return context


class SaleCreateView(SalesAccessMixin, CompanyQuerysetMixin, CreateView):
	model = Sale
	form_class = SaleForm
	template_name = "ventas/sale_form.html"
	success_url = reverse_lazy("ventas:list")

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["company"] = getattr(self.request, "company", None) or getattr(self.request.user, "company", None)
		return kwargs

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = None
		company = getattr(request, "company", None) or getattr(request.user, "company", None)
		if not company:
			messages.error(request, "Tu usuario no tiene una empresa asociada para registrar ventas.")
			return render(request, self.template_name, self.get_context_data(form=self.get_form(), formset=SaleDetailFormSet(instance=self.object)))
		form = self.get_form()
		formset = SaleDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save(commit=False)
			self.object.seller = request.user
			self.object.company = company
			self.object.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			if self.object.status == self.object.STATUS_CONFIRMED:
				from caja.models import CashBox
				CashBox.validate_day_open(self.object.date, self.object.company)
				try:
					self.object.apply_inventory_output()
				except ValidationError as exc:
					messages.error(request, str(exc))
					self.object.delete()
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				CashBox.register_sale(self.object)
				messages.success(request, "Venta registrada exitosamente.")
			else:
				messages.success(request, "Proforma guardada exitosamente.")

			return redirect(self.success_url)

		return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = SaleDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = SaleDetailFormSet(instance=self.object)
		products_qs = Product.objects.select_related("brand", "category").filter(is_active=True)
		if self.request.company:
			products_qs = products_qs.filter(company=self.request.company)
		kwargs["products_data"] = [
			{
				"id": product.id,
				"code": product.code or "",
				"name": product.name,
				"price": float(product.price),
				"stock": product.stock,
				"brand": product.brand.name,
				"category": product.category.name,
				"size": product.size,
				"color": product.color,
				"image": product.image.url if product.image else "",
			}
			for product in products_qs
		]
		return super().get_context_data(**kwargs)


class SaleUpdateView(SalesAccessMixin, CompanyQuerysetMixin, UpdateView):
	model = Sale
	form_class = SaleForm
	template_name = "ventas/sale_form.html"
	success_url = reverse_lazy("ventas:list")

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["company"] = self.request.company
		return kwargs

	def get(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status != Sale.STATUS_PROFORMA:
			messages.error(request, "Solo se pueden editar ventas en estado proforma.")
			return redirect(self.success_url)
		return super().get(request, *args, **kwargs)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		if self.object.status != Sale.STATUS_PROFORMA:
			messages.error(request, "Solo se pueden editar ventas en estado proforma.")
			return redirect(self.success_url)

		form = self.get_form()
		formset = SaleDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			new_status = form.cleaned_data.get("status")
			self.object = form.save(commit=False)
			self.object.save()
			formset.instance = self.object
			formset.save()
			self.object.calculate_total()

			if new_status == Sale.STATUS_CONFIRMED:
				from caja.models import CashBox
				CashBox.validate_day_open(self.object.date, self.object.company)
				try:
					self.object.apply_inventory_output()
				except ValidationError as exc:
					messages.error(request, str(exc))
					return render(request, self.template_name, self.get_context_data(form=form, formset=formset))
				CashBox.register_sale(self.object)
				messages.success(request, "Proforma confirmada como venta exitosamente.")
			else:
				messages.success(request, "Proforma actualizada exitosamente.")

			return redirect(self.success_url)

		return render(request, self.template_name, self.get_context_data(form=form, formset=formset))

	def get_context_data(self, **kwargs):
		if self.request.POST:
			kwargs["formset"] = SaleDetailFormSet(self.request.POST, instance=self.object)
		else:
			kwargs["formset"] = SaleDetailFormSet(instance=self.object)
		products_qs = Product.objects.select_related("brand", "category").filter(is_active=True)
		if self.request.company:
			products_qs = products_qs.filter(company=self.request.company)
		kwargs["products_data"] = [
			{
				"id": product.id,
				"code": product.code or "",
				"name": product.name,
				"price": float(product.price),
				"stock": product.stock,
				"brand": product.brand.name,
				"category": product.category.name,
				"size": product.size,
				"color": product.color,
				"image": product.image.url if product.image else "",
			}
			for product in products_qs
		]
		kwargs["is_edit"] = True
		return super().get_context_data(**kwargs)


class SaleDeleteView(SalesAccessMixin, CompanyQuerysetMixin, DeleteView):
	model = Sale
	template_name = "ventas/sale_confirm_delete.html"
	success_url = reverse_lazy("ventas:list")

	def get(self, request, *args, **kwargs):
		if not request.user.is_admin:
			messages.error(request, "Solo un administrador puede anular ventas.")
			return redirect(self.success_url)
		return super().get(request, *args, **kwargs)

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		if not request.user.is_admin:
			messages.error(request, "Solo un administrador puede anular ventas.")
			return redirect(self.success_url)

		self.object = self.get_object()
		if self.object.status == self.object.STATUS_CANCELED:
			messages.info(request, "La venta ya se encuentra anulada.")
			return redirect(self.success_url)

		if self.object.status == self.object.STATUS_CONFIRMED:
			from caja.models import CashBox
			try:
				CashBox.validate_day_open(company=self.object.company)
			except ValidationError as exc:
				messages.error(request, str(exc))
				return redirect(self.success_url)
			self.object.restore_inventory_output()
			CashBox.register_sale_reversal(self.object)
			messages.warning(request, "Venta anulada y stock restaurado.")
		else:
			messages.warning(request, "Proforma anulada.")

		self.object.status = self.object.STATUS_CANCELED
		self.object.canceled_by = request.user
		self.object.canceled_at = timezone.now()
		self.object.save(update_fields=["status", "canceled_by", "canceled_at", "updated_at"])
		return redirect(self.success_url)


class SalePDFView(SalesAccessMixin, View):
	def get(self, request, pk, *args, **kwargs):
		sale = Sale.objects.select_related("client", "company", "seller").get(pk=pk)
		if request.company and sale.company_id != request.company.id:
			return redirect("ventas:list")
		details = sale.saledetail_set.select_related("product").all()
		context = {
			"sale": sale,
			"details": details,
			"company": sale.company,
			"now": timezone.localtime(),
		}
		filename = f"venta_{sale.id}.pdf"
		return render_to_pdf("ventas/sale_pdf.html", context, filename=filename, base_url=request.build_absolute_uri("/"))
