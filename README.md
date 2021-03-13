# app_podemosaprender

Para escribir acá y compartir en las redes, pero ser dueñes de nuestro contenido.

El primer paso es que se pueda escribir un post. Seguí los pasos del [tutorial de DjangoGirls](https://tutorial.djangogirls.org/es/django_start_project/) que seguimos juntos en el grupo. 

1. Cree pa_site como sito
2. Elegí idioma español PERO deje la TIME_ZONE en UTC pq en el grupo hay personas de varios países y lo mejor va a ser mostrar en la UI las fechas y horas como las convierta su navegador de UTC a la que tengan configurada.
3. Cree pa_charlas_app como app
4. Cree un modelo Texto más simple que el Post del tutorial y seguí los otros pasos hasta poder crear uno desde el admin.
5. Agregue link para compartir en Facebook y copiar al portapapeles
6. Agregue login con Facebook y runserver_plus de Django extensions
7. Agregue bootstrap en la plantilla base.html y los [botones de redes sociales](http://lipis.github.io/bootstrap-social/)

8. Hice demasiados cambios en los modelos y no pude migrar!
   agregue un script para borrar todas las migraciones, la base, y empezar de cero en pa_lib_py/bin/migrations_delete.sh
   lo ejecute, borre la base, hice makemigrations y migrate

### Para usar y seguir desarrollando

Despues de extraer localmente este proyecto con git clone

pip -r requirements.dev.txt #A: instala lo que necesitas para desarrollar

### Para usar el login con facebook y google

Tenes que crear una app en la consola de facebook, habilitar la funcion Login, y sacar de ahi el AppId=KEY y el Secret. Los pones en un archivo .env.json en la carpeta del proyecto

~~~ .env.json
{
	"SECRET_KEY": "LaClaveSecretaQueGeneraDjangoEnSettingsVaAca-djahd",
	"SOCIAL_AUTH_FACEBOOK_KEY": "112233445566778", 
	"SOCIAL_AUTH_FACEBOOK_SECRET": "112233445566778899aabbccddeeff00",
	"SOCIAL_AUTH_GOOGLE_KEY": "11223344556-112233445566778899aabbccddeeffgg.apps.googleusercontent.com",
	"SOCIAL_AUTH_GOOGLE_SECRET": "i2iu7hajhas-Wndkakhh12lm"
}
~~~

Despues podes ejecutar un servidor https con

~~~
python manage.py runserver_plus --cert-file tmpcert.crt
~~~

### Cuando desplegue en un hosting

Tuve que usar mariadb en vez de sqlite, asi que agregue la configuracion de la db a .env.json que queda asi:

~~~ .env.json
{
	"SECRET_KEY": "LaClaveSecretaQueGeneraDjangoEnSettingsVaAca-djahd",
	"SOCIAL_AUTH_FACEBOOK_KEY": "112233445566778", 
	"SOCIAL_AUTH_FACEBOOK_SECRET": "112233445566778899aabbccddeeff00",
	"DB": {
		"ENGINE": "django.db.backends.mysql",
		"NAME": "mibase",
		"USER": "miuser",
		"PASSWORD": "miclavesecreta",
		"HOST": "servidorconladb",
		"PORT": ""
	}
}
~~~

Tuve que agregar la url de autenticacion en la consola de facebook en Settings de Facebook Login (que no son los mismos que para la app, estan mas abajo)

https://si.podemosaprender.org/social-auth/complete/facebook/


Lo mismo con la de google donde agregue

https://si.podemosaprender.org/social-auth/complete/google-oauth2/

(cuando lo probas local tenes que agregar tambien por ej https://127.0.0.1:8000/social-auth/complete/google-oauth2/ )


## Para más adelante

Un editor con preview para los textos usando Markdown? https://neutronx.github.io/django-markdownx/
