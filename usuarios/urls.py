from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("usuarios/", views.CompanyUserListView.as_view(), name="user_list"),
    path("usuarios/nuevo/", views.CompanyUserCreateView.as_view(), name="user_create"),
    path("usuarios/<int:pk>/editar/", views.CompanyUserUpdateView.as_view(), name="user_update"),
    path("usuarios/<int:pk>/eliminar/", views.CompanyUserDeleteView.as_view(), name="user_delete"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("perfil/", views.profile_view, name="profile"),
    path("password-change/", views.PasswordChangeView.as_view(), name="password_change"),
    path(
        "password-change/done/",
        views.PasswordChangeDoneView.as_view(),
        name="password_change_done",
    ),
]
