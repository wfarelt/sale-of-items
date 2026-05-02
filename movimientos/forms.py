from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from productos.models import Product

from .models import InventoryMovement, InventoryMovementDetail


class InventoryMovementManualForm(forms.ModelForm):
    class Meta:
        model = InventoryMovement
        fields = ["type", "description"]
        widgets = {
            "type": forms.Select(attrs={"class": "form-select"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["description"].required = True


class InventoryMovementDetailForm(forms.ModelForm):
    class Meta:
        model = InventoryMovementDetail
        fields = ["product", "quantity"]
        widgets = {
            "product": forms.Select(attrs={"class": "form-select"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0.01"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = Product.objects.filter(is_active=True).order_by("name")


class BaseInventoryMovementDetailFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        movement_type = (self.data.get("type") or "").strip()
        selected_products = {}

        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue

            product = form.cleaned_data.get("product")
            quantity = form.cleaned_data.get("quantity")
            if not product or not quantity:
                continue

            if product.pk in selected_products:
                raise ValidationError("No puedes repetir el mismo producto en un movimiento manual.")

            selected_products[product.pk] = quantity

            if movement_type == InventoryMovement.TYPE_OUT and product.stock < quantity:
                raise ValidationError(f"Stock insuficiente para {product.name}.")


InventoryMovementDetailFormSet = inlineformset_factory(
    InventoryMovement,
    InventoryMovementDetail,
    form=InventoryMovementDetailForm,
    formset=BaseInventoryMovementDetailFormSet,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True,
)
