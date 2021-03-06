"""blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path,re_path,include
from django.views.static import serve
from blog import settings
from app01 import views as app_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('weixin', app_views.weixin_main),
    path('login/', app_views.log_in, name='login'),
    path('logout/', app_views.log_out, name='logout'),
    path('register/', app_views.register, name='register'),
    path('index/', app_views.index),
    path('get_valid_img/', app_views.get_valid_img, name='get_valid_img'),
    re_path(r'^$', app_views.index),
    re_path(r'blog/',include('app01.urls')),
    # media配置
    re_path(r'media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
