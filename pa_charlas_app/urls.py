from django.contrib.auth.decorators import login_required
from django.urls import path
from . import views

urlpatterns = [
	path("login/", views.login, name="login"),

	path('charla/', views.CharlaListView.as_view(), name='charla_list' ),
	#A: el alma de la aplicacion son las "charlas"

	path('charla/nueva', login_required(views.texto_edit), name='texto_new'),
	#A: crear una charla es simplemente escribir un texto con hashtags, hay uno automatico para casuales

	path('charla/<int:charla_pk>/nuevo', login_required(views.texto_edit), name='charla_texto_nuevo'),
	path('charla/<int:charla_pk>/<int:pk>', login_required(views.texto_edit), name='charla_texto_edit'),
	#A: las charlas estan hechas de textos
	path('texto/<int:pk>', views.texto_detail, name='texto_detail'),
	#A: hay un link para el texto asi lo compartimos en redes

	path('charla/<int:pk>/', views.charla_texto_list, name='charla_texto_list_k'),
	path('charla/<str:charla_titulo>/', views.charla_texto_list, name='charla_texto_list_t'),
	#A: en general miramos charlas por id o por titulo

	#S: la home page es algun tipo de lista de charlas
	path('', views.CharlaListView.as_view(), name='home'),

	# : lista de usuarios
	path('usuario/', views.usuario_list, name='usuario_list'), #TODO: poner login_required?

	path('usuario/<int:pk>/', views.usuario_texto_list, name='usuario_texto_list_k'), #TODO: poner login_required?
]
