from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, View

from config.pdf_utils import render_to_pdf
from empresas.models import Company
from productos.models import Product

from .forms import InventoryMovementDetailFormSet, InventoryMovementManualForm
from .models import InventoryMovement


class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_almacen


class InventoryAdminAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin


class InventoryMovementListView(InventoryAccessMixin, ListView):
	model = InventoryMovement
	template_name = "movimientos/movement_list.html"
	context_object_name = "movements"
	paginate_by = 25

	def get_queryset(self):
		queryset = super().get_queryset().select_related("registered_by").prefetch_related("details__product")
		search = self.request.GET.get("q", "").strip()
		movement_type = self.request.GET.get("type", "").strip()
		product_id = self.request.GET.get("product", "").strip()

		if search:
			queryset = queryset.filter(
				Q(details__product__name__icontains=search)
				| Q(details__product__code__icontains=search)
				| Q(reference__icontains=search)
				| Q(description__icontains=search)
			)

		if movement_type in {InventoryMovement.TYPE_IN, InventoryMovement.TYPE_OUT}:
			queryset = queryset.filter(type=movement_type)

		if product_id:
			queryset = queryset.filter(details__product_id=product_id)

		return queryset.distinct()

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "")
		context["selected_type"] = self.request.GET.get("type", "")
		context["selected_product"] = self.request.GET.get("product", "")
		products_qs = Product.objects.order_by("name")
		context["products"] = products_qs
		for movement in context["movements"]:
			movement.total_quantity_value = movement.total_quantity()
		return context


class InventoryMovementManualCreateView(InventoryAdminAccessMixin, CreateView):
	model = InventoryMovement
	form_class = InventoryMovementManualForm
	template_name = "movimientos/movement_form.html"
	success_url = reverse_lazy("movimientos:list")

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		if self.request.POST:
			context["formset"] = InventoryMovementDetailFormSet(self.request.POST, instance=self.object)
		else:
			context["formset"] = InventoryMovementDetailFormSet(instance=self.object)
		return context

	@transaction.atomic
	def post(self, request, *args, **kwargs):
		self.object = None
		form = self.get_form()
		formset = InventoryMovementDetailFormSet(request.POST, instance=self.object)

		if form.is_valid() and formset.is_valid():
			self.object = form.save(commit=False)
			self.object.reference = "Ajuste por inventario"
			self.object.registered_by = request.user
			self.object.save()

			formset.instance = self.object
			formset.save()

			for detail in self.object.details.select_related("product"):
				product = detail.product
				if self.object.type == InventoryMovement.TYPE_IN:
					product.stock += detail.quantity
				else:
					if product.stock < detail.quantity:
						raise ValidationError(f"Stock insuficiente para {product.name}.")
					product.stock -= detail.quantity
				product.save(update_fields=["stock", "updated_at"])

			messages.success(request, "Movimiento manual registrado correctamente.")
			return redirect(self.success_url)

		return self.render_to_response(self.get_context_data(form=form, formset=formset))


class InventoryMovementDetailView(InventoryAccessMixin, DetailView):
	model = InventoryMovement
	template_name = "movimientos/movement_detail.html"
	context_object_name = "movement"

	def get_queryset(self):
		return super().get_queryset().select_related("registered_by").prefetch_related("details__product")


class InventoryMovementPDFView(InventoryAccessMixin, View):
	def get(self, request, pk, *args, **kwargs):
		movement = InventoryMovement.objects.select_related("registered_by").prefetch_related("details__product").get(pk=pk)
		context = {
			"movement": movement,
			"company": Company.get_solo(),
			"now": timezone.localtime(),
		}
		filename = f"movimiento_{movement.id}.pdf"
		return render_to_pdf("movimientos/movement_pdf.html", context, filename=filename, base_url=request.build_absolute_uri("/"))

