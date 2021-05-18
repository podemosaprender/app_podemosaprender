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
9. Cree una migracion par cargar datos con `python manage.py makemigrations --empty pa_charlas_app` y agregue una llamada para crearlos
10. Simplifique plantillas, cree un fragmento con los botones para compartir p_compartir_botons.html que se puede incluir en cualquier lado, y una funcion para usar en las plantillas (se pueden crear mas)
11. [Braian Martino](https://www.linkedin.com/in/braian-martino-770704198/) agrego la lista y textos de cada usuario (de primera!)
12. Configure django_restframework y jwt token para que el el futuro se puedan consumir y cargar datos ej. desde una SPA javascript en la web o cordova (mas info abajo).
14. Configure CORS para que se pueda usar la API REST desde cualquier lado (gracias [Braian Martino](https://www.linkedin.com/in/braian-martino-770704198/)!) como dice en [django-cors-headers](https://github.com/adamchainz/django-cors-headers)
15. Con Brian agregamos que los textos se muestran como markdown usando marked en el browser
16. Agregue las url que buscan palabras en los titulos de las charlas como /t/banda que busca %banda% y /t/sabado/enero que busca %sabado%enero% . Cree un operador de busqueda like para eso

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

### Podés usar Docker para luchar menos con las dependencias

La primera vez construis tu contenedor con 
~~~
docker build -t pa_app .
~~~

Después lo ejecutás con
~~~
docker run -it --rm -v "$(pwd)":/pa_app/ -p 8000:8000 pa_app bash 
~~~

Para ejecutar el servidor
~~~
docker run -it --rm -v "$(pwd)":/pa_app/ -p 8000:8000 pa_app /scripts/docker/docker_start.sh
~~~

Si tenés linux mint o ubuntu y te da error, tal vez tengas que ejecutar [estos comandos](https://www.digitalocean.com/community/questions/how-to-fix-docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket)

### Desplegar en Heroku

Si bajaste este repo los archivos ya están listos y no necesitas editar nada. Abajo cuento como hice para que nos quede.

Después de clonar este repositorio, entre a la carpeta donde está este README y ejecuté

~~~
heroku login #A: para entrar con mi usuario
heroku apps:create #A: creo la aplicacion (una vez)
git push heroku main #A: subo el codigo, cada vez que lo cambio, despues de hacer commit
heroku run python manage.py migrate #A: actualizo la DB postgress cada vez que cambio models
heroku run python manage.py createsuperuser #A: una vez
heroku apps:info #A: para ver y abrir la url donde se desplegó
heroku pg:psql #A: para acceder como admin a la base de datos
~~~

Si accedes a la base de datos podés consultar por ej

~~~
select * from pa_charlas_app_texto;
~~~

Podríamos tener datos de prueba y [subirlos como dice aquí](https://devcenter.heroku.com/articles/heroku-postgres-import-export)


#### Como hice (sirve para otras apps Django)

Tomando información de [estas instrucciones](https://devcenter.heroku.com/articles/getting-started-with-python) edité

* Procfile
* pa_site/settings.py
* requirements.txt

y puse DEBUG true en .env.json
~~~
{
	"SECRET_KEY": "LaClaveSecretaQueGeneraDjangoEnSettingsVaAca-djahd",
	"SOCIAL_AUTH_FACEBOOK_KEY": "112233445566778", 
	"SOCIAL_AUTH_FACEBOOK_SECRET": "112233445566778899aabbccddeeff00",
	"SOCIAL_AUTH_GOOGLE_KEY": "11223344556-112233445566778899aabbccddeeffgg.apps.googleusercontent.com",
	"SOCIAL_AUTH_GOOGLE_SECRET": "i2iu7hajhas-Wndkakhh12lm",
	"ALLOWED_HOSTS": ["127.0.0.1","localhost"],
	"DEBUG": true
}
~~~

Sin eso __no funciona gunicorn__ , hay algún problema con los archivos estáticos como explican en [este hilo en stackoverflow](https://stackoverflow.com/questions/44160666/valueerror-missing-staticfiles-manifest-entry-for-favicon-ico/51060143#51060143) junto con soluciones más generales.

También funcionó poniendo en Procfile

~~~
web: python manage.py runserver 0.0.0.0:$PORT
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
		"OPTIONS": {"charset": "utf8mb4"},
		"NAME": "mibase",
		"USER": "miuser",
		"PASSWORD": "miclavesecreta",
		"HOST": "servidorconladb",
		"PORT": ""
	}
}
~~~

Tuve que cambiar la columna texto para que acepte unicode de 4 bytes para los emoji, entre directo con mysql desde la consola y ejecuté

~~~
alter table pa_charlas_app_texto CHANGE texto texto longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
~~~


Tuve que agregar la url de autenticacion en la consola de facebook en Settings de Facebook Login (que no son los mismos que para la app, estan mas abajo)

https://si.podemosaprender.org/social-auth/complete/facebook/


Lo mismo con la de google donde agregue

https://si.podemosaprender.org/social-auth/complete/google-oauth2/

(cuando lo probas local tenes que agregar tambien por ej https://127.0.0.1:8000/social-auth/complete/google-oauth2/ )

### Usando la API REST

Por ahora la podes probar obteniendo un token con
~~~
curl -X POST -H "Content-Type: application/json" -d '{"username":"tuusuario", "password": "tuclave"}' http://127.0.0.1:8000/api/token/
~~~

Lo podes usar como en [este ejemplo](https://rest-api-token.glitch.me/)

OjO! en hostm1 que tiene python 3.6.8 tuve que hacer un _downgrade_ de PyJWT, asi
~~~
pip install -r requirements.txt
pip install PyJWT==1.7.1
~~~

puso unos carteles avisando que otro paquete necesita la version 2.0 pero no hay que hacerles caso porque esa es la version de PyJWT que no anda en esta de Python

### Optimizar acceso a la base de datos

En el shell podes activar que muestre (log) los accesos y consultas con

~~~
import logging
logger = logging.getLogger('django.db.backends')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())
~~~

## Calendario y hashtags

Queremos que sea fácil escribir qué día organizás una actividad  

Queremos que sea fácil mostrar un calendario  

Patrones para los titulos de charla  

~~~
dia_
dia_sabado_1ro_cada_mes
dia_sabado_2do_cada_mes
dia_sabado_1_antes_fin_de_mes
dia_sabado_antes_fin_de_mes
dia_sabado_de_enero

dia_23_marzo_2021_13hs
dia_lunes_a_viernes_19hs
dia_lunes_miercoles_viernes_19hs

dia_sabado_1ro_marzo
dia_sabado_1ro_junio_julio
dia_sabado_1ro_marzo_a_junio
~~~

## Para más adelante

Un editor con preview para los textos usando Markdown? https://neutronx.github.io/django-markdownx/


## Borrar datos de prueba

~~~
python manage.py runscript -v3 mantenimiento.borrar_borrames
~~~
