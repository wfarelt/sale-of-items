from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import redirect, get_object_or_404, render
from .models import Proveedor
from .forms import ProveedorForm

class SupplierAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_admin


class ProveedorListView(SupplierAccessMixin, ListView):
    model = Proveedor
    template_name = "proveedores/proveedor_list.html"
    context_object_name = "proveedores"
    paginate_by = 10

    def get_queryset(self):
        return Proveedor.objects.all().order_by("nombre")

class ProveedorCreateView(SupplierAccessMixin, CreateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "proveedores/proveedor_form.html"
    success_url = reverse_lazy("proveedores:list")

class ProveedorUpdateView(SupplierAccessMixin, UpdateView):
    model = Proveedor
    form_class = ProveedorForm
    template_name = "proveedores/proveedor_form.html"
    success_url = reverse_lazy("proveedores:list")


# Nueva vista para deshabilitar proveedor

class ProveedorDisableView(SupplierAccessMixin, View):
    template_name = "proveedores/proveedor_confirm_delete.html"

    def get(self, request, pk):
        proveedor = get_object_or_404(Proveedor, pk=pk)
        return render(request, self.template_name, {"object": proveedor})

    def post(self, request, pk):
        proveedor = get_object_or_404(Proveedor, pk=pk)
        proveedor.activo = not proveedor.activo
        proveedor.save()
        return redirect("proveedores:list")
