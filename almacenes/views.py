from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, View
from django.shortcuts import redirect, get_object_or_404, render
from .models import Almacen
from .forms import AlmacenForm

class AlmacenAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return user.is_admin or user.is_almacen

class AlmacenListView(AlmacenAccessMixin, ListView):
    model = Almacen
    template_name = "almacenes/almacen_list.html"
    context_object_name = "almacenes"
    paginate_by = 10

    def get_queryset(self):
        return Almacen.objects.all().order_by("nombre")

class AlmacenCreateView(AlmacenAccessMixin, CreateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = "almacenes/almacen_form.html"
    success_url = reverse_lazy("almacenes:list")

    def form_valid(self, form):
            form.instance.company = self.request.company
            return super().form_valid(form)

class AlmacenUpdateView(AlmacenAccessMixin, UpdateView):
    model = Almacen
    form_class = AlmacenForm
    template_name = "almacenes/almacen_form.html"
    success_url = reverse_lazy("almacenes:list")


# Vista para deshabilitar almacén
class AlmacenDisableView(AlmacenAccessMixin, View):
    template_name = "almacenes/almacen_confirm_delete.html"

    def get(self, request, pk):
        almacen = get_object_or_404(Almacen, pk=pk)
        return render(request, self.template_name, {"object": almacen})

    def post(self, request, pk):
        almacen = get_object_or_404(Almacen, pk=pk)
        almacen.activo = not almacen.activo
        almacen.save()
        if almacen.activo:
            messages.success(request, "Almacén activado correctamente.")
        else:
            messages.warning(request, "Almacén desactivado correctamente.")
        return redirect("almacenes:list")
