from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('nodes/<slug:uuid>', views.nodes, name='nodes'),
    path('delete/<slug:uuid>', views.delete, name='delete'),
    path('imports', views.imports, name='imports'),
    path('sales/<str:date>', views.sales, name='sales'),
    path('node/<slug:uuid>/statistic/', views.stats, name='stats'),
    # path('test/', views.test, name='test'),
]
