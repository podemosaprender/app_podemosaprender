from django.urls import path
from . import views

urlpatterns = [
	path('', views.texto_list, name='texto_list'),
	path('texto/<int:pk>/', views.texto_detail, name='texto_detail'),
]
