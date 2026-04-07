from django.urls import path

from .views import (
    BrandCreateView,
    BrandDeleteView,
    BrandListView,
    BrandUpdateView,
    CategoryCreateView,
    CategoryDeleteView,
    CategoryListView,
    CategoryUpdateView,
    ProductCreateView,
    ProductDeleteView,
    ProductListView,
    ProductUpdateView,
)

app_name = "productos"

urlpatterns = [
    path("", ProductListView.as_view(), name="list"),
    path("nuevo/", ProductCreateView.as_view(), name="create"),
    path("<int:pk>/editar/", ProductUpdateView.as_view(), name="update"),
    path("<int:pk>/eliminar/", ProductDeleteView.as_view(), name="delete"),
    path("categorias/", CategoryListView.as_view(), name="categories"),
    path("categorias/nueva/", CategoryCreateView.as_view(), name="category_create"),
    path("categorias/<int:pk>/editar/", CategoryUpdateView.as_view(), name="category_update"),
    path("categorias/<int:pk>/eliminar/", CategoryDeleteView.as_view(), name="category_delete"),
    path("marcas/", BrandListView.as_view(), name="brands"),
    path("marcas/nueva/", BrandCreateView.as_view(), name="brand_create"),
    path("marcas/<int:pk>/editar/", BrandUpdateView.as_view(), name="brand_update"),
    path("marcas/<int:pk>/eliminar/", BrandDeleteView.as_view(), name="brand_delete"),
]
