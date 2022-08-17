from os import name
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.urls import path, re_path, include
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

from django.views.decorators.csrf import csrf_exempt

from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from graphene_django.views import GraphQLView

from .views import views, views_avisos
from . import views_rest

rest_router = routers.DefaultRouter()
rest_router.register('participante', views_rest.ParticipanteViewSet, basename='user')
rest_router.register('charla', views_rest.CharlaViewSet, basename='charla')
rest_router.register('texto', views_rest.TextoViewSet)
rest_router.register('charlaitem', views_rest.CharlaItemViewSet)
#A: agregamos las vistas rest al router asi las muestra en la UI

urlpatterns = [
	path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
	path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
	path('api/token/user/', views_rest.token_user, name='token_user'),
	#A: autenticacion de la api REST o GraphQL

	path('api/', include(rest_router.urls)), #A: api REST

	path("graphql/", csrf_exempt(GraphQLView.as_view(graphiql=True))), #A: api graphql

	path("login/", views.login, name="login"),
	path('clave/', login_required(views.UserPassCambiar), name="user_pass_cambiar"),
	path('login/clave/', auth_views.LoginView.as_view(template_name='pa_charlas_app/user_login_form.html'), name="user_login"),

	path("facebook_delete_data/", views.FacebookDataDeletionView.as_view(), name="facebook_delete_data"),
	path("facebook_delete_data_check/<str:code>/", views.FacebookDataDeletionCheckView.as_view(), name="facebook_delete_data_check"),
	#A: login desde la UI web

	path('charla/', views.CharlaQueSigoListView.as_view(), name='charla_quesigo_list' ),
	path('charla/todas', views.CharlaListView.as_view(), name='charla_list' ),
	#A: el alma de la aplicacion son las "charlas"

	path('charla/nueva', login_required(views.texto_edit), name='texto_new'),
	#A: crear una charla es simplemente escribir un texto con hashtags, hay uno automatico para casuales

	path('charla/<int:charla_pk>/nuevo', login_required(views.texto_edit), name='charla_texto_nuevo'),
	path('charla/<str:charla_titulo>/nuevo', login_required(views.texto_edit), name='charla_texto_nuevo_s'),
	path('charla/<int:charla_pk>/<int:pk>', login_required(views.texto_edit), name='charla_texto_edit'),
	#A: las charlas estan hechas de textos

	path('imagen/<str:imagen_titulo>', login_required(views.imagen_edit), name='imagen_edit'),

	path('texto/', views.texto_list, name='texto_list'),

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

	path('donde-nombran-a/<str:username>/', views.usuario_textos_que_nombran, name='usuario_textos_que_nombran'),
	path('como/', login_required(views.usuario_plan), name='usuario_plan'), 
	path('como/<str:username>/', login_required(views.usuario_plan), name='usuario_plan'), 

	path('banco/',login_required(views.banco_list), name='banco_list'),
	re_path(r't/(?P<un_path>.*)/$', views.CharlaComoPathListView.as_view(), name='charla_como_path'),
	#A: ej. t/sabado/cada_mes para buscar titulos que digan sabado y cada_mes

	path('', views.texto_list, name='home'),
	#A: la home page es la lista de textos nuevos

	#S: Avisos ############################
	path('aviso/', views_avisos.AvisoListView.as_view(), name='aviso_list'),
	path('aviso/<int:pk>/', views_avisos.AvisoDetailView.as_view(), name='aviso_detail'),
	path('aviso/mios/', login_required(views_avisos.AvisoMiosListView.as_view()), name='aviso_user_list'),
	path('aviso/nuevo/', login_required(views_avisos.AvisoFormView.as_view()), name='aviso_new'),
	path('aviso/nuevo/<int:pk>/',login_required(views_avisos.AvisoUpdateView.as_view()), name='aviso_edit'),


]


if settings.IS_DEVEL_SERVER: #A: solo en desarrollo local! sino, configurar ej. nginx
	urlpatterns+= static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) #A: imagenes subidas 
