# app_podemosaprender

Para escribir acá y compartir en las redes, pero ser dueñes de nuestro contenido.

El primer paso es que se pueda escribir un post. Seguí los pasos del [tutorial de DjangoGirls](https://tutorial.djangogirls.org/es/django_start_project/) que seguimos juntos en el grupo. 

1. Cree pa_site como sito
2. Elegí idioma español PERO deje la TIME_ZONE en UTC pq en el grupo hay personas de varios países y lo mejor va a ser mostrar en la UI las fechas y horas como las convierta su navegador de UTC a la que tengan configurada.
3. Cree pa_charlas_app como app
4. Cree un modelo Texto más simple que el Post del tutorial y seguí los otros pasos hasta poder crear uno desde el admin.
5. Agregue link para compartir en Facebook y copiar al portapapeles
6. Agregue login con Facebook y runserver_plus de Django extensions

### Para usar y seguir desarrollando

Despues de extraer localmente este proyecto con git clone

pip -r requirements.dev.txt #A: instala lo que necesitas para desarrollar

### Para usar el login con facebook 

Tenes que crear una app en la consola de facebook, habilitar la funcion Login, y sacar de ahi el AppId=KEY y el Secret. Los pones en un archivo .env.json en la carpeta del proyecto

~~~ .env.json
{
	"SECRET_KEY": "LaClaveSecretaQueGeneraDjangoEnSettingsVaAca-djahd",
	"SOCIAL_AUTH_FACEBOOK_KEY": "112233445566778", 
	"SOCIAL_AUTH_FACEBOOK_SECRET": "112233445566778899aabbccddeeff00"
}
~~~

Despues podes ejecutar un servidor https con

~~~
python manage.py runserver_plus --cert-file tmpcert.crt
~~~
