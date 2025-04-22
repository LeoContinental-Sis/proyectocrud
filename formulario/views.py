# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Tarea
from .forms import TareaForm

def listar_tareas(request):
    tareas = Tarea.objects.all()
    return render(request, 'formulario/listar_tareas.html', {'tareas': tareas})

def crear_tarea(request):
    if request.method == 'POST':
        form = TareaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_tareas')
    else:
        form = TareaForm()
    return render(request, 'formulario/crear_tareas.html', {'form': form})

def editar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    if request.method == 'POST':
        form = TareaForm(request.POST, instance=tarea)
        if form.is_valid():
            form.save()
            return redirect('listar_tareas')
    else:
        form = TareaForm(instance=tarea)
    return render(request, 'formulario/editar_tarea.html', {'form': form, 'tarea': tarea})

def eliminar_tarea(request, tarea_id):
    tarea = get_object_or_404(Tarea, pk=tarea_id)
    tarea.delete()
    return redirect('listar_tareas')