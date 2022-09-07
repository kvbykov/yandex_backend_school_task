from django.urls import path
from . import views


urlpatterns = [
    path('nodes/<slug:uuid>', views.get_unit, name='get_unit'),
    path('delete/<slug:uuid>', views.delete, name='delete'),
    path('imports', views.import_units, name='import_units'),
    path('sales/<str:request_date>', views.get_recently_updated, name='get_recently_updated'),
    path('node/<slug:uuid>/statistic/', views.get_statistics, name='get_statistics'),
]
