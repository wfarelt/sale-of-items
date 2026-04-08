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
            "size",
            "color",
            "brand",
            "category",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "stock": forms.NumberInput(attrs={"class": "form-control"}),
            "size": forms.Select(attrs={"class": "form-select"}),
            "color": forms.TextInput(attrs={"class": "form-control"}),
            "brand": forms.Select(attrs={"class": "form-select"}),
            "category": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        self.fields["brand"].queryset = Brand.objects.filter(is_active=True).order_by("name")
        self.fields["category"].queryset = Category.objects.filter(is_active=True).order_by("name")

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
