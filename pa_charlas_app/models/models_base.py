from django.db import models


class BaseModel(models.Model):
    """
    Modelo base del cual van a heredar todos los modelos.
    Te registra la fecha de cuando fue creado y modificado
    Y ademas ejecuta el clean del modelo antes de guardarlo,
    algo que django no hace por defecto.
    """
    class Meta:
        abstract = True
    
    fh_creado = models.DateTimeField(
        'creado a las ',
        auto_now_add=True,
        help_text='Fecha y hora en qeu el modelo fue creado'
    )
    fh_modificado = models.DateTimeField(
        'modificado a las ',
        auto_now=True,
        help_text='Fecha y hora en qeu el modelo fue editado'
    )

    def save(self, *args, **kwargs):
        self.clean()
        super(BaseModel, self).save(*args, **kwargs)
