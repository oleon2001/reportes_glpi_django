from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('tecnicos/', views.obtener_tecnicos, name='obtener_tecnicos'),
    path('generar-reporte/', views.generar_reporte, name='generar_reporte'),
    path('tickets-reabiertos/', views.tickets_reabiertos, name='tickets_reabiertos'),
]