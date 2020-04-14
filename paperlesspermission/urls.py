"""paperlesspermission URL Configuration

Copyright 2020 Mark Stenglein, The Paperless Permission Authors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('import/', views.djo_import_all, name='import all'),
    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('admin/', admin.site.urls),
    path('login/', auth_views.LoginView.as_view(
        template_name='paperlesspermission/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view()),
    path('slip/<slug:slip_id>/', views.slip, name='permission slip'),
    path('trip/', views.trip_list, name='trip list'),
    path('trip/new/', views.new_trip, name='new field trip'),
    path('trip/<int:trip_id>/', views.trip_detail, name='trip detail'),
    path('trip/<int:trip_id>/status', views.trip_status, name='trip status'),
    path('trip/<int:trip_id>/approve/', views.approve_trip, name='approve trip'),
    path('trip/<int:trip_id>/archive/', views.archive_trip, name='archive trip'),
    path('trip/<int:trip_id>/release/', views.release_trip, name='release trip emails'),
    path('slip/<int:slip_id>/reset/', views.slip_reset, name='reset permission slip'),
    path('slip/<int:slip_id>/resend/', views.slip_resend, name='resend permission slip'),
]
