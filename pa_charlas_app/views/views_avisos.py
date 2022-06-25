"""
Ver vistas genericas de Django: (para ahorrarme codigo)
https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-display/
https://docs.djangoproject.com/en/4.0/ref/class-based-views/generic-editing/
"""
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormView, UpdateView
from django.shortcuts import redirect


from pa_charlas_app.models import AvisoModel
from pa_charlas_app.forms import AvisoForm


class AvisoListView(ListView):
    template_name= 'pa_charlas_app/avisos/aviso_list.html'
    queryset=  AvisoModel.objects.order_by('fh_modificado').all()
    paginate_by = 20  
    extra_context= {
        'type_name': 'aviso',
        'type_url_base': 'aviso',
        'create_url': '/aviso/nuevo', #A: url a la que va a direccionar el boton 'Crear Aviso'
        'titulo': 'Avisos',
        'vista_detalle': 'aviso_detail',
    }
    def get_queryset(self):
        queryset = super().get_queryset()
        autor_id = self.request.GET.get('autor')
        if autor_id: # A: el usuario estar buscando avisos por autor
            return queryset.filter(autor_id=autor_id)
        return queryset

class AvisoDetailView(DetailView):
    model = AvisoModel
    template_name = 'pa_charlas_app/avisos/aviso_detail.html'
    extra_context= {
		'return_url': '/aviso/',
    }

class AvisoFormView(FormView):
    form_class = AvisoForm
    template_name = 'pa_charlas_app/base_edit.html'
    success_url = '/aviso/'

    def form_valid(self, form):
        form.instance.autor = self.request.user
        form.save()
        return super().form_valid(form)
    
class AvisoUpdateView(UpdateView):
    template_name = 'pa_charlas_app/base_edit.html'
    form_class = AvisoForm
    model = AvisoModel
    success_url = '/aviso/'

    def form_valid(self, form):
        if form.instance.autor == self.request.user or self.request.user.is_staff: #A: tiene permiso para editar
            form.save()
            self.success_url = f'/aviso/{form.instance.pk}'
            return super().form_valid(form)
        return redirect('/aviso/') #TODO: mostrar mensaje de error: no tenes permisos