from django.urls import path
from . import views

urlpatterns = [
	path('', views.texto_list, name='texto_list'),
	path('texto/new', views.texto_edit, name='texto_new'),
	path('texto/<int:pk>/', views.texto_detail, name='texto_detail'),
	path('texto/<int:pk>/edit/', views.texto_edit, name='texto_edit'),
]
