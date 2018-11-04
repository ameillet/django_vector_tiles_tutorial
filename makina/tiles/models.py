from django.contrib.gis.db import models


class Departement(models.Model):
    code_dept = models.CharField(max_length=2)
    nom_dept = models.CharField(max_length=100)
    geom = models.MultiPolygonField(srid=3857)
