import math
import mapbox_vector_tile
import mercantile
from django.contrib.gis.db.models.functions import Intersection
from django.contrib.gis.geos import Polygon
from django.http import HttpResponse
from tiles.models import Departement


def pixel_length(zoom):
    """
    Return the length (in meters) for a pixel for a given zoom.

    When the zoom increases, the pixel length diminishes. 

    Args:
        zoom (int): level of zoom for this tile
    Returns:
        float: length (in meters ??) of a pixel

    """
    RADIUS = 6378137
    CIRCUM = 2 * math.pi * RADIUS
    SIZE = 512
    return CIRCUM / (SIZE / 2 ** int(zoom))


def tile_view(request, zoom, x, y):
    """
    Returns an MVT tiles given zoom, x and y in TMS format

    References:
        https://www.mapbox.com/vector-tiles/
        http://wiki.osgeo.org/wiki/Tile_Map_Service_Specification#global-mercator

    """
    bounds = mercantile.bounds(int(x), int(y), int(zoom))
    west, south = mercantile.xy(bounds.west, bounds.south)
    east, north = mercantile.xy(bounds.east, bounds.north)

    pixel = pixel_length(zoom)
    buffer = 4 * pixel
    bbox = Polygon.from_bbox((
        west - buffer,
        south - buffer,
        east + buffer,
        north + buffer
    ))

    departements = Departement.objects.filter(geom__intersects=bbox)
    departements = departements.annotate(clipped=Intersection('geom', bbox))

    tile = {
        "name": "departements",
        "features": [
            {
                "geometry": departement.clipped.simplify(
                    pixel,
                    preserve_topology=True
                ).wkt,
                "properties": {
                    "numero": departement.code_dept,
                    "nom": departement.nom_dept,
                },
            }
            for departement in departements
        ],
    }
    vector_tile = mapbox_vector_tile.encode(tile, quantize_bounds=(
        west, south, east, north
    ))
    return HttpResponse(
        vector_tile, content_type="application/vnd.mapbox-vector-tile")
