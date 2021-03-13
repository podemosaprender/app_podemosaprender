from django.urls import path
from . import views

urlpatterns = [
	path("login/", views.login, name="login"),

	path('', views.CharlaListView.as_view(), name='home'),
	path('texto/nuevo/', views.texto_edit, name='texto_new'),
	path('texto/<int:pk>/edit/', views.texto_edit, name='texto_edit'),

	path('charla/', views.CharlaListView.as_view(), name='charla_list' ),
	path('charla/new', views.CharlaCreateView.as_view(), name='charla_new' ),
	path('charla/X/<int:pk>/', views.CharlaUpdateView.as_view(), name='charla_edit' ),

	path('charla/<int:charla_pk>/nuevo', views.texto_edit, name='charla_texto_nuevo'),
	path('charla/<int:pk>/', views.charla_texto_list, name='charla_texto_list_k'),
	path('charla/<str:charla_titulo>/', views.charla_texto_list, name='charla_texto_list_t'),
]
