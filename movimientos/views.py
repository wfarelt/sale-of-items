from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.views.generic import DetailView, ListView

from productos.models import Product

from .models import InventoryMovement


class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		return self.request.user.is_admin or self.request.user.is_almacen


class InventoryMovementListView(InventoryAccessMixin, ListView):
	model = InventoryMovement
	template_name = "movimientos/movement_list.html"
	context_object_name = "movements"
	paginate_by = 25

	def get_queryset(self):
		queryset = InventoryMovement.objects.prefetch_related("details__product")
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
		context["products"] = Product.objects.order_by("name")
		for movement in context["movements"]:
			movement.total_quantity_value = movement.total_quantity()
		return context


class InventoryMovementDetailView(InventoryAccessMixin, DetailView):
	model = InventoryMovement
	template_name = "movimientos/movement_detail.html"
	context_object_name = "movement"

	def get_queryset(self):
		return InventoryMovement.objects.prefetch_related("details__product")
