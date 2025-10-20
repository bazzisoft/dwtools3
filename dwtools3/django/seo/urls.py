from django.urls import path
from . import views


urlpatterns = [
    path(
        "admin/seo/metatags-admin-redirect/",
        views.seo_metatags_admin_redirect,
        name="seo_metatags_admin_redirect",
    ),
]
