from pathlib import Path
import os

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Chave secreta do Django (mantenha em segredo em produção!)
SECRET_KEY = 'django-insecure-+6p0smn_=q0-yxbh(8x*hc&_7+h6quu#u=i(%1%(tii*lzpjn5'

# 🚨 Segurança: Desative `DEBUG` em produção!
DEBUG = True

# Hosts permitidos
ALLOWED_HOSTS = ['*']

# 📌 Aplicações registradas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Apps do projeto
    'app',
    'clientes',
    'estetica',
    'plastica',
]

# 📌 Middlewares (proteções e funcionalidades do Django)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 📌 Configuração das URLs principais
ROOT_URLCONF = 'app.urls'

# 📌 Configuração dos templates (HTMLs)
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['app/templates'],  # Diretório dos templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 📌 Configuração do WSGI
WSGI_APPLICATION = 'app.wsgi.application'

# 📌 Configuração do banco de dados (SQLite por padrão)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# 📌 Validação de senhas (Recomendado para segurança)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 📌 Configuração de arquivos de mídia (imagens, PDFs, etc.)
MEDIA_URL = '/media/'  # URL onde os arquivos serão servidos
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Diretório onde os arquivos serão salvos

# 📌 Configuração de arquivos estáticos (CSS, JS, imagens)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Diretório onde os arquivos estáticos serão coletados
STATIC_URL = '/static/'

# ✅ Corrigindo erro do STATICFILES_DIRS
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static') if os.path.exists(os.path.join(BASE_DIR, 'static')) else None
]
STATICFILES_DIRS = [path for path in STATICFILES_DIRS if path is not None]  # Remove `None` se não existir

# 📌 Internacionalização e fuso horário
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# 📌 Definição do tipo padrão de chave primária
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ✅ Configuração de autenticação
LOGIN_URL = '/login/'  # Redireciona usuários não autenticados para a tela de login
LOGIN_REDIRECT_URL = '/'  # Página inicial após login
LOGOUT_REDIRECT_URL = '/login/'  # Após logout, volta para a tela de login

# ✅ Configuração para autenticação (email ou username)
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ✅ Configuração da sessão (tempo de expiração)
SESSION_COOKIE_AGE = 1800  # Sessão expira em 30 minutos
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Expira ao fechar o navegador
SESSION_SAVE_EVERY_REQUEST = True  # Atualiza o tempo da sessão a cada requisição
