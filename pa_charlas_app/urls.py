from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
	path("login/", views.login, name="login"),

	#S: el alma de la aplicacion son las "charlas"
	path('charla/', views.CharlaListView.as_view(), name='charla_list' ),
	path('charla/nueva', login_required(views.CharlaCreateView.as_view()), name='charla_new' ),
	

	path('charla/<int:charla_pk>/nuevo', views.texto_edit, name='charla_texto_nuevo'),
	path('charla/<int:pk>/', views.charla_texto_list, name='charla_texto_list_k'),
	path('charla/<str:charla_titulo>/', views.charla_texto_list, name='charla_texto_list_t'),

	#S: las charlas estan hechas de textos
	path('texto/nuevo/', login_required(views.texto_edit), name='texto_new'),
	path('texto/<int:pk>/edit/', login_required(views.texto_edit), name='texto_edit'),

	#S: la home page es algun tipo de lista de charlas
	path('', views.CharlaListView.as_view(), name='home'),
]
