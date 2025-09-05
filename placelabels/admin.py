from django.contrib import admin
from .models import ObjType, PlaceLabel, Objects
# Register your models here.
admin.site.register(ObjType)
admin.site.register(PlaceLabel)
admin.site.register(Objects)
