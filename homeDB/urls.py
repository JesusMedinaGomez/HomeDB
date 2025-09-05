"""
URL configuration for homeDB project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from placelabels import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('objetos/', views.objects, name='objects'),
    path('objetos/crear', views.create_obj, name='create_obj'),
    path('objetos/editar/<int:pk>/', views.edit_object, name='edit_object'),
    path("objetos/delete/<int:pk>/", views.delete_object, name="delete_object"),
    path('objetos/<int:pk>/', views.object_detail, name='object_detail'),
    path('lugares/', views.places, name='places'),
    path('lugares/crear', views.create_place, name='create_place'),
    path('lugares/editar/<int:pk>/', views.edit_place, name='edit_place'),
    path("lugares/delete/<int:pk>/", views.delete_place, name="delete_place"),
    path('tipo_objetos/', views.objtypes, name='objtypes'),
    path('tipo_objetos/crear', views.create_objtype, name='create_objtype'),
    path('tipo_objetos/editar/<int:pk>/', views.edit_objtype, name='edit_objtype'),
    path("tipo_objetos/delete/<int:pk>/", views.delete_objtype, name="delete_objtype"),
    path('objetos/crear/ajax/place/', views.create_place_ajax, name='create_place_ajax'),
    path('objetos/crear/ajax/type/', views.create_objtype_ajax, name='create_objtype_ajax'),
    path('logout/', views.mylogout, name='logout'),
    path('login/', views.mylogin, name='login')
]
