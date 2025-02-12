from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_invalid(self, form):
        """Exibir mensagem de erro caso o login falhe"""
        messages.error(self.request, "Usuário ou senha inválidos. Tente novamente.")
        return super().form_invalid(form)

    def get_success_url(self):
        """Redireciona para o dashboard após login"""
        return reverse_lazy('dashboard')

class CustomLogoutView(LogoutView):
    """Redireciona para a tela de login após o logout"""
    next_page = reverse_lazy('login')

@login_required
def dashboard(request):
    """Exibir a página de Dashboard"""
    return render(request, 'dashboard.html')
