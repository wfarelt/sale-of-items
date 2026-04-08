from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
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
