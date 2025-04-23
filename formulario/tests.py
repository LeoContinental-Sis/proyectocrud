from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from .models import Tarea
from .forms import TareaForm
import factory

# Factories para crear datos de prueba
class TareaFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tarea
    
    titulo = "Tarea de prueba"
    descripcion = "Descripción de prueba"

# Pruebas para modelos
class ModelTests(TestCase):
    def test_creacion_tarea(self):
        """Test de creación básica de tarea"""
        tarea = TareaFactory()
        self.assertEqual(tarea.titulo, "Tarea de prueba")
        self.assertTrue(isinstance(tarea, Tarea))
        self.assertEqual(str(tarea), tarea.titulo)
    
    def test_campos_requeridos(self):
        """Test que verifica campos requeridos"""
        with self.assertRaises(Exception):
            Tarea.objects.create(titulo=None)
    
    def test_campos_opcionales(self):
        """Test que verifica campos no requeridos"""
        tarea = Tarea.objects.create(titulo="Tarea sin descripción")
        self.assertIsNone(tarea.descripcion)

# Pruebas para formularios
class FormTests(TestCase):
    def test_form_valido(self):
        """Test de formulario válido"""
        form_data = {
            'titulo': 'Tarea válida',
            'descripcion': 'Descripción válida'
        }
        form = TareaForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_invalido_sin_titulo(self):
        """Test de formulario inválido (falta título)"""
        form_data = {
            'titulo': '',
            'descripcion': 'Descripción válida'
        }
        form = TareaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)
    
    def test_form_titulo_max_length(self):
        """Test de longitud máxima del título"""
        form_data = {
            'titulo': 'a' * 101,  # Más del límite de 100 caracteres
            'descripcion': 'Descripción válida'
        }
        form = TareaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('titulo', form.errors)

# Pruebas para vistas
class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.tarea = TareaFactory()
        self.urls = {
            'listar': reverse('listar_tareas'),
            'crear': reverse('crear_tareas'),
            'editar': reverse('editar_tarea', args=[self.tarea.id]),
            'eliminar': reverse('eliminar_tarea', args=[self.tarea.id]),
        }
    
    def test_listar_tareas_vista(self):
        """Test de vista listar_tareas"""
        response = self.client.get(self.urls['listar'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/listar_tareas.html')
        self.assertContains(response, self.tarea.titulo)
    
    def test_listar_tareas_vacia(self):
        """Test de vista listar_tareas sin tareas"""
        Tarea.objects.all().delete()
        response = self.client.get(self.urls['listar'])
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay tareas creadas.")
    
    def test_crear_tarea_get(self):
        """Test de GET a crear_tarea"""
        response = self.client.get(self.urls['crear'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/crear_tareas.html')
        self.assertIsInstance(response.context['form'], TareaForm)
    
    def test_crear_tarea_post_valido(self):
        """Test de POST válido a crear_tarea"""
        data = {
            'titulo': 'Nueva tarea',
            'descripcion': 'Nueva descripción'
        }
        response = self.client.post(self.urls['crear'], data)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.assertEqual(Tarea.objects.count(), 2)  # La de factory + nueva
    
    def test_crear_tarea_post_invalido(self):
        """Test de POST inválido a crear_tarea"""
        data = {
            'titulo': '',  # Inválido
            'descripcion': 'Descripción'
        }
        response = self.client.post(self.urls['crear'], data)
        self.assertEqual(response.status_code, 200)  # Vuelve a mostrar el form
        self.assertFormError(response, 'form', 'titulo', 'Este campo es obligatorio.')
    
    def test_editar_tarea_get(self):
        """Test de GET a editar_tarea"""
        response = self.client.get(self.urls['editar'])
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'formulario/editar_tarea.html')
        self.assertEqual(response.context['tarea'], self.tarea)
    
    def test_editar_tarea_post_valido(self):
        """Test de POST válido a editar_tarea"""
        data = {
            'titulo': 'Tarea editada',
            'descripcion': 'Descripción editada'
        }
        response = self.client.post(self.urls['editar'], data)
        self.assertEqual(response.status_code, 302)  # Redirección
        self.tarea.refresh_from_db()
        self.assertEqual(self.tarea.titulo, 'Tarea editada')
    
    def test_eliminar_tarea(self):
        """Test de eliminar_tarea"""
        tarea_id = self.tarea.id
        response = self.client.post(self.urls['eliminar'])
        self.assertEqual(response.status_code, 302)  # Redirección
        with self.assertRaises(Tarea.DoesNotExist):
            Tarea.objects.get(pk=tarea_id)

# Pruebas de integración
class IntegrationTests(TestCase):
    def test_flujo_completo(self):
        """Test de flujo completo CRUD"""
        client = Client()
        
        # 1. Listar tareas (vacío)
        list_url = reverse('listar_tareas')
        response = client.get(list_url)
        self.assertContains(response, "No hay tareas creadas.")
        
        # 2. Crear tarea
        create_url = reverse('crear_tareas')
        response = client.post(create_url, {
            'titulo': 'Tarea de integración',
            'descripcion': 'Descripción de prueba'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        tarea = Tarea.objects.first()
        self.assertEqual(tarea.titulo, 'Tarea de integración')
        
        # 3. Editar tarea
        edit_url = reverse('editar_tarea', args=[tarea.id])
        response = client.post(edit_url, {
            'titulo': 'Tarea editada',
            'descripcion': 'Descripción editada'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        tarea.refresh_from_db()
        self.assertEqual(tarea.titulo, 'Tarea editada')
        
        # 4. Eliminar tarea
        delete_url = reverse('eliminar_tarea', args=[tarea.id])
        response = client.post(delete_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Tarea.objects.count(), 0)
        
