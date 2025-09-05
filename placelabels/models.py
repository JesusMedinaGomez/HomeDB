from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import unicodedata

# Función para quitar acentos
def strip_accents(text):
    """
    Elimina acentos de una cadena de texto.
    """
    return ''.join(c for c in unicodedata.normalize('NFD', text)
                   if unicodedata.category(c) != 'Mn')


class ObjType(models.Model):
    typename = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'typename')  # Clave única por usuario

    def save(self, *args, **kwargs):
        # Guardar el nombre en mayúsculas y sin acentos
        self.typename = strip_accents(self.typename).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.typename


class PlaceLabel(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pseudonym = models.CharField(max_length=10, blank=True)  # Nuevo campo

    class Meta:
        unique_together = ('user', 'name')  # Clave única por usuario

    def save(self, *args, **kwargs):
        # Guardar el nombre en mayúsculas y sin acentos
        self.name = strip_accents(self.name).upper()

        # Generar pseudónimo si no existe
        if not self.pseudonym:
            first_letter = self.name[0].upper()
            count = PlaceLabel.objects.filter(user=self.user, name__startswith=first_letter).count()
            self.pseudonym = f"{first_letter}{count + 1}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.pseudonym})"


class Objects(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    label = models.ForeignKey(
        ObjType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    placelabel = models.ForeignKey(
        PlaceLabel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    datereg = models.DateTimeField(default=timezone.now)
    important = models.BooleanField(default=False)
    isInPlace = models.BooleanField(default=True)
    hasIt = models.CharField(max_length=100, null=True, blank=True, default="Yo")
    whoIsIt = models.CharField(max_length=100, null=True, default="Yo")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

