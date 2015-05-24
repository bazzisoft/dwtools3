from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^admin/seo/metatags-admin-redirect/$', views.seo_metatags_admin_redirect, name='seo_metatags_admin_redirect'),
]
