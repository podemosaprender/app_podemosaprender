from django.urls import path
from . import views

urlpatterns = [
	path('', views.texto_list, name='texto_list'),
]
