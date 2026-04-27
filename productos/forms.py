from django import forms

from .models import Brand, Category, Product


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
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "formato": forms.TextInput(attrs={"class": "form-control"}),
            "indicaciones_uso": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "metros_cuadrados_por_caja": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "acabado": forms.TextInput(attrs={"class": "form-control"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "stock_minimo": forms.NumberInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.company = kwargs.pop("company", None)
        super().__init__(*args, **kwargs)
        brand_qs = Brand.objects.filter(is_active=True).order_by("name")
        category_qs = Category.objects.filter(is_active=True).order_by("name")
        if self.company:
            brand_qs = brand_qs.filter(company=self.company)
            category_qs = category_qs.filter(company=self.company)
        self.fields["brand"].queryset = brand_qs
        self.fields["category"].queryset = category_qs

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
