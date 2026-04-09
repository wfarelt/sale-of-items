from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from empresas.mixins import CompanyQuerysetMixin
from .forms import BrandForm, CategoryForm, ProductForm
from .models import Brand, Category, Product


class InventoryAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
	def test_func(self):
		user = self.request.user
		return user.is_admin or user.is_almacen


class ProductListView(InventoryAccessMixin, CompanyQuerysetMixin, ListView):
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


class ProductCreateView(InventoryAccessMixin, CompanyQuerysetMixin, CreateView):
	model = Product
	form_class = ProductForm
	template_name = "productos/product_form.html"
	success_url = reverse_lazy("productos:list")

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["user"] = self.request.user
		kwargs["company"] = self.request.company
		return kwargs


class ProductUpdateView(InventoryAccessMixin, CompanyQuerysetMixin, UpdateView):
	model = Product
	form_class = ProductForm
	template_name = "productos/product_form.html"
	success_url = reverse_lazy("productos:list")

	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs["user"] = self.request.user
		kwargs["company"] = self.request.company
		return kwargs


class ProductDeleteView(InventoryAccessMixin, CompanyQuerysetMixin, DeleteView):
	model = Product
	template_name = "productos/product_confirm_delete.html"
	success_url = reverse_lazy("productos:list")

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.is_active = not self.object.is_active
		self.object.save(update_fields=["is_active", "updated_at"])
		if self.object.is_active:
			messages.success(request, "Producto activado correctamente.")
		else:
			messages.warning(request, "Producto desactivado correctamente.")
		return redirect(self.success_url)


class CategoryListView(InventoryAccessMixin, CompanyQuerysetMixin, ListView):
	model = Category
	template_name = "productos/category_list.html"
	context_object_name = "categories"


class CategoryCreateView(InventoryAccessMixin, CompanyQuerysetMixin, CreateView):
	model = Category
	form_class = CategoryForm
	template_name = "productos/category_form.html"
	success_url = reverse_lazy("productos:categories")


class CategoryUpdateView(InventoryAccessMixin, CompanyQuerysetMixin, UpdateView):
	model = Category
	form_class = CategoryForm
	template_name = "productos/category_form.html"
	success_url = reverse_lazy("productos:categories")


class CategoryDeleteView(InventoryAccessMixin, CompanyQuerysetMixin, DeleteView):
	model = Category
	template_name = "productos/category_confirm_delete.html"
	success_url = reverse_lazy("productos:categories")

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.is_active = not self.object.is_active
		self.object.save(update_fields=["is_active"])
		if self.object.is_active:
			messages.success(request, "Categoria activada correctamente.")
		else:
			messages.warning(request, "Categoria desactivada correctamente.")
		return redirect(self.success_url)



class BrandListView(InventoryAccessMixin, CompanyQuerysetMixin, ListView):
	model = Brand
	template_name = "productos/brand_list.html"
	context_object_name = "brands"


class BrandCreateView(InventoryAccessMixin, CompanyQuerysetMixin, CreateView):
	model = Brand
	form_class = BrandForm
	template_name = "productos/brand_form.html"
	success_url = reverse_lazy("productos:brands")


class BrandUpdateView(InventoryAccessMixin, CompanyQuerysetMixin, UpdateView):
	model = Brand
	form_class = BrandForm
	template_name = "productos/brand_form.html"
	success_url = reverse_lazy("productos:brands")


class BrandDeleteView(InventoryAccessMixin, CompanyQuerysetMixin, DeleteView):
	model = Brand
	template_name = "productos/brand_confirm_delete.html"
	success_url = reverse_lazy("productos:brands")

	def post(self, request, *args, **kwargs):
		self.object = self.get_object()
		self.object.is_active = not self.object.is_active
		self.object.save(update_fields=["is_active"])
		if self.object.is_active:
			messages.success(request, "Marca activada correctamente.")
		else:
			messages.warning(request, "Marca desactivada correctamente.")
		return redirect(self.success_url)
