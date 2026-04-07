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
