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
        self.typename = strip_accents(self.typename).upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.typename


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # <-- agregar esto

    class Meta:
        unique_together = ('user', 'name')  # cada usuario puede tener habitaciones con nombres únicos
    def __str__(self):
        return self.name


class PlaceLabel(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    pseudonym = models.CharField(max_length=20, blank=True)

    # Eliminamos cualquier restricción de unicidad
    # class Meta:
    #     unique_together = ('user', 'name')  <-- eliminado

    def save(self, *args, **kwargs):
        self.name = strip_accents(self.name).upper()

        if not self.pseudonym:
            if self.room and self.room.name:
                room_prefix = ''.join(word[0] for word in self.room.name.split()).upper()
            else:
                room_prefix = "XX"

            place_prefix = ''.join(word[0] for word in self.name.split()).upper()
            # Contamos cuántos lugares hay con el mismo nombre en la misma habitación
            count = PlaceLabel.objects.filter(room=self.room, name=self.name).count() + 1
            self.pseudonym = f"{room_prefix}{place_prefix}{count}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.pseudonym})"



class BoxLabel(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    place = models.ForeignKey(PlaceLabel, on_delete=models.CASCADE, related_name="boxes")
    pseudonym = models.CharField(max_length=20, blank=True)

    class Meta:
        unique_together = ('user', 'name')

    def save(self, *args, **kwargs):
        self.name = strip_accents(self.name).upper()

        if not self.pseudonym:
            # Buscar cuántos boxlabels tiene ya ese place
            count = BoxLabel.objects.filter(user=self.user, place=self.place).count() + 1
            self.pseudonym = f"C{count}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.pseudonym}"

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
    boxlabel = models.ForeignKey(  # <-- nuevo campo
        BoxLabel,
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

