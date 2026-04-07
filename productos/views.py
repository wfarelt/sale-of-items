from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import BrandForm, CategoryForm, ProductForm
from .models import Brand, Category, Product


class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		user = self.request.user
		return user.is_admin or user.is_almacen


class ProductListView(InventoryAccessMixin, ListView):
	model = Product
	template_name = "productos/product_list.html"
	context_object_name = "products"
	paginate_by = 10

	def get_queryset(self):
		queryset = super().get_queryset().select_related("category", "brand")
		search = self.request.GET.get("q", "").strip()

		if search:
			queryset = queryset.filter(
				Q(name__icontains=search)
				| Q(description__icontains=search)
				| Q(color__icontains=search)
				| Q(category__name__icontains=search)
				| Q(brand__name__icontains=search)
			)

		return queryset

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context["search_query"] = self.request.GET.get("q", "").strip()
		return context


class ProductCreateView(InventoryAccessMixin, CreateView):
	model = Product
	form_class = ProductForm
	template_name = "productos/product_form.html"
	success_url = reverse_lazy("productos:list")


class ProductUpdateView(InventoryAccessMixin, UpdateView):
	model = Product
	form_class = ProductForm
	template_name = "productos/product_form.html"
	success_url = reverse_lazy("productos:list")


class ProductDeleteView(InventoryAccessMixin, DeleteView):
	model = Product
	template_name = "productos/product_confirm_delete.html"
	success_url = reverse_lazy("productos:list")


class CategoryListView(InventoryAccessMixin, ListView):
	model = Category
	template_name = "productos/category_list.html"
	context_object_name = "categories"


class CategoryCreateView(InventoryAccessMixin, CreateView):
	model = Category
	form_class = CategoryForm
	template_name = "productos/category_form.html"
	success_url = reverse_lazy("productos:categories")


class CategoryUpdateView(InventoryAccessMixin, UpdateView):
	model = Category
	form_class = CategoryForm
	template_name = "productos/category_form.html"
	success_url = reverse_lazy("productos:categories")


class CategoryDeleteView(InventoryAccessMixin, DeleteView):
	model = Category
	template_name = "productos/category_confirm_delete.html"
	success_url = reverse_lazy("productos:categories")


class BrandListView(InventoryAccessMixin, ListView):
	model = Brand
	template_name = "productos/brand_list.html"
	context_object_name = "brands"


class BrandCreateView(InventoryAccessMixin, CreateView):
	model = Brand
	form_class = BrandForm
	template_name = "productos/brand_form.html"
	success_url = reverse_lazy("productos:brands")


class BrandUpdateView(InventoryAccessMixin, UpdateView):
	model = Brand
	form_class = BrandForm
	template_name = "productos/brand_form.html"
	success_url = reverse_lazy("productos:brands")


class BrandDeleteView(InventoryAccessMixin, DeleteView):
	model = Brand
	template_name = "productos/brand_confirm_delete.html"
	success_url = reverse_lazy("productos:brands")
