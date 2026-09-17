"""
URL configuration for crop_site project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django import views
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from recommender.views import admin_login, home, signup, prediction, login_view, history, profile, logout_view, dashboard, users, change_password, edit_profile, user_details, terms_privacy

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", home, name="home"),
    path("signup/", signup, name="signup"),
    path("login/", login_view, name="login"),
    path("prediction/", prediction, name="prediction"),
    path("history/", history, name="history"),
    path("profile/", profile, name="profile"),
    path("edit-profile/", edit_profile, name="edit_profile"),
    path("logout/", logout_view, name="logout"),
    path("dashboard/", dashboard, name="dashboard"),
    path("users/", users, name="users"),
    path("change-password/", change_password, name="change_password"),
    path("admin-login/", admin_login, name="admin_login"),
    path("user/<int:user_id>/",user_details,name="user_details"),
    path("terms-privacy/", terms_privacy, name="terms_privacy"),
   # path("create-admin-secret-123/", create_admin, name="create_admin"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

