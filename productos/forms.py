from django import forms

from .models import Acabado, Brand, Category, Formato, IndicacionesUso, M2Caja, Product


class ProductForm(forms.ModelForm):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={"class": "form-control"}),
        label="Código",
    )

    class Meta:
        model = Product
        fields = [
            "code",
            "name",
            "description",
            "price",
            "image",
            "stock",
            "formato",
            "indicaciones_uso",
            "metros_cuadrados_por_caja",
            "acabado",
            "color",
            "brand",
            "category",
            "stock_minimo",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "0"}),
            "formato": forms.Select(attrs={"class": "form-select"}),
            "indicaciones_uso": forms.Select(attrs={"class": "form-select"}),
            "metros_cuadrados_por_caja": forms.Select(attrs={"class": "form-select"}),
            "acabado": forms.Select(attrs={"class": "form-select"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        brand_qs = Brand.objects.filter(is_active=True).order_by("name")
        category_qs = Category.objects.filter(is_active=True).order_by("name")
        formato_qs = Formato.objects.filter(is_active=True).order_by("name")
        acabado_qs = Acabado.objects.filter(is_active=True).order_by("name")
        indicaciones_qs = IndicacionesUso.objects.filter(is_active=True).order_by("name")
        m2caja_qs = M2Caja.objects.filter(is_active=True).order_by("value")
        
        self.fields["brand"].queryset = brand_qs
        self.fields["category"].queryset = category_qs
        self.fields["formato"].queryset = formato_qs
        self.fields["acabado"].queryset = acabado_qs
        self.fields["indicaciones_uso"].queryset = indicaciones_qs
        self.fields["metros_cuadrados_por_caja"].queryset = m2caja_qs

        user_can_manage_values = bool(
            self.user and self.user.is_authenticated and (self.user.is_admin or self.user.is_almacen)
        )
        if not user_can_manage_values:
            self.fields["price"].disabled = True
            self.fields["stock"].disabled = True

    def clean(self):
        cleaned_data = super().clean()

        user_can_manage_values = bool(
            self.user and self.user.is_authenticated and (self.user.is_admin or self.user.is_almacen)
        )
        if not user_can_manage_values:
            changed_fields = set(getattr(self, "changed_data", []))
            if {"price", "stock"}.intersection(changed_fields):
                raise forms.ValidationError("Solo admin y almacen pueden modificar precio y stock.")

        return cleaned_data


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class FormatoForm(forms.ModelForm):
    class Meta:
        model = Formato
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class AcabadoForm(forms.ModelForm):
    class Meta:
        model = Acabado
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}


class IndicacionesUsoForm(forms.ModelForm):
    class Meta:
        model = IndicacionesUso
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class M2CajaForm(forms.ModelForm):
    class Meta:
        model = M2Caja
        fields = ["value"]
        widgets = {
            "value": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ["name"]
        widgets = {"name": forms.TextInput(attrs={"class": "form-control"})}
