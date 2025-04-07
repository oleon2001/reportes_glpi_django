import json
from django.shortcuts import render
from django.http import JsonResponse
from .services import ReportGenerator
import re

def index(request):
    return render(request, 'metricas/index.html')

def obtener_tecnicos(request):
    try:
        tecnicos = ReportGenerator.obtener_tecnicos()
        return JsonResponse({'tecnicos': tecnicos})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def generar_reporte(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else request.POST
            fecha_ini = data.get('fecha_ini')
            fecha_fin = data.get('fecha_fin')
            
            # Manejar diferentes formatos de técnicos
            tecnicos = data.get('tecnicos', '[]')
            if isinstance(tecnicos, str):
                tecnicos = json.loads(data.get('tecnicos', '[]'))
                if isinstance(tecnicos, str):  # Por si llega como string
                    tecnicos = json.loads(tecnicos)
            
            # Validar fechas
            if not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_ini) or not re.match(r'^\d{4}-\d{2}-\d{2}$', fecha_fin):
                return JsonResponse({'error': 'Formato de fecha inválido (YYYY-MM-DD)'}, status=400)

            resultados = ReportGenerator.generar_reporte_principal(fecha_ini, fecha_fin, tecnicos)
            return JsonResponse({'data': resultados})
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Formato de datos inválido'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)

def tickets_reabiertos(request):
    if request.method == 'POST':
        try:
            data = request.POST
            tecnico = data.get('tecnico')
            fecha_ini = data.get('fecha_ini')
            fecha_fin = data.get('fecha_fin')

            tickets = ReportGenerator.obtener_tickets_reabiertos(tecnico, fecha_ini, fecha_fin)
            return JsonResponse({'data': tickets})
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Método no permitido'}, status=405)