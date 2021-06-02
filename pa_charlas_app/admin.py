from django.contrib import admin
from .models import Texto, TipoCharla, Charla, Voto, BancoTx

admin.site.register(Texto)
admin.site.register(TipoCharla)
admin.site.register(Charla)
admin.site.register(Voto)
admin.site.register(BancoTx)
