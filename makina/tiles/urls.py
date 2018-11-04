from django.urls import path

from . import views

app_name = 'tiles'

urlpatterns = [
    path('<int:zoom>/<int:x>/<int:y>.mvt', views.tile_view, name='tile'),
]