from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include

from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from . import views
from . import views_rest

rest_router = routers.DefaultRouter()
rest_router.register('participante', views_rest.ParticipanteViewSet, basename='user')
rest_router.register('charla', views_rest.CharlaViewSet, basename='charla')
rest_router.register('texto', views_rest.TextoViewSet)
#A: agregamos las vistas rest al router asi las muestra en la UI

urlpatterns = [
	path('api/', include(rest_router.urls)),
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	#A: documentacion y autenticacion de la api REST

	path("login/", views.login, name="login"),
	path("facebook_delete_data/", views.FacebookDataDeletionView.as_view(), name="facebook_delete_data"),
	path("facebook_delete_data_check/<str:code>/", views.FacebookDataDeletionCheckView.as_view(), name="facebook_delete_data_check"),
	#A: login desde la UI web

	path('charla/', views.CharlaQueSigoListView.as_view(), name='charla_quesigo_list' ),
	path('charla/todas', views.CharlaListView.as_view(), name='charla_list' ),
	#A: el alma de la aplicacion son las "charlas"

	path('charla/nueva', login_required(views.texto_edit), name='texto_new'),
	#A: crear una charla es simplemente escribir un texto con hashtags, hay uno automatico para casuales

	path('charla/<int:charla_pk>/nuevo', login_required(views.texto_edit), name='charla_texto_nuevo'),
	path('charla/<int:charla_pk>/<int:pk>', login_required(views.texto_edit), name='charla_texto_edit'),
	#A: las charlas estan hechas de textos
	path('texto/<int:pk>', views.texto_detail, name='texto_detail'),
	path('texto/<int:pk>/img.png', views.texto_img, name='texto_img'),
	#A: hay un link para el texto asi lo compartimos en redes

	path('charla/<int:pk>/', views.charla_texto_list, name='charla_texto_list_k'),
	path('charla/<str:charla_titulo>/', views.charla_texto_list, name='charla_texto_list_t'),
	#A: en general miramos charlas por id o por titulo

	path('evento/', views.evento_list, name='evento_list'),
	path('evento/ical/', views.evento_list_ical, name='evento_list_ical'),
	#A: Agenda de eventos

	path('usuario/', views.usuario_list, name='usuario_list'), #TODO: poner login_required?
	path('usuario/<int:pk>/', views.usuario_texto_list, name='usuario_texto_list_k'), #TODO: poner login_required?
	#A: lista de usuarios

	re_path(r't/(?P<un_path>.*)/$', views.CharlaComoPathListView.as_view(), name='charla_como_path'),
	#A: ej. t/sabado/cada_mes para buscar titulos que digan sabado y cada_mes

	path('', views.CharlaQueSigoListView.as_view(), name='home'),
	#A: la home page es algun tipo de lista de charlas
]
