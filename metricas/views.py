import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from .services import ReportGenerator
import re
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.http import require_http_methods

@ensure_csrf_cookie
@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('index')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        if not username or not password:
            messages.error(request, 'Por favor, ingrese su usuario y contraseña.')
            return render(request, 'metricas/login.html')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'index')
            return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos. Por favor, intente nuevamente.')
    
    return render(request, 'metricas/login.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def index(request):
    return render(request, 'metricas/index.html')

@login_required
def obtener_tecnicos(request):
    try:
        tecnicos = ReportGenerator.obtener_tecnicos()
        return JsonResponse({'tecnicos': tecnicos})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def generar_reporte(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.body else request.POST
            fecha_ini = data.get('fecha_ini')
            fecha_fin = data.get('fecha_fin')
            
            # Manejar la selección de todos los técnicos
            if data.get('seleccionar_todos', False):
                tecnicos = ReportGenerator.obtener_tecnicos()
            else:
                tecnicos = data.get('tecnicos', '[]')
                if isinstance(tecnicos, str):
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

@login_required
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