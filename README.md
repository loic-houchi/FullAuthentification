# Full Authentication Tutorial (Login, Register, Logout & Reset Password)

This tutorial will teach you about authentication and registration in Django.

---

## Getting Started

### 1- Create a project directory
```bash
# Create a directory for your project and move into it
mkdir my_django_project
cd my_django_project
```

### 2- Set up a python virtual Environment
```bash
# create a virtual environement called "venv"
python3 -m venv venv

# Activate the virtual environmment
source venv/bin/activate

# Deactivate environment
deactivate

# Reactivate
source venv/bin/activate
```

### 3- Install Django
```bash
# Install Django in your virtual environment
pip install django

# Confirm Django installation
django-admin --version
```

### 4- Create the Django project and App
```bash
# Create a Django project named AuthenticationProject
django-admin startproject AuthenticationProject

# Move into project directory
cd AuthenticationProject

# Create an app called Coreapp
python manage.py startapp Coreapp
```

- Open the project in your code editor
- Create a `templates` folder and register it in the project settings
- Register the app in the project settings
- Create URLs for the app and register them in the project's URLs
- Setup static files in `settings.py`

```python
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Dossier où Django va collecter tous les fichiers statiques (pour la production)
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Dossier(s) où tu mets tes fichiers statiques en développement
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
```

---

## Getting Templates files from the Github repository

Download the following HTML templates from GitHub:  
- `index.html`
- `login.html`
- `register.html`
- `forgot_password.html`
- `password_reset_sent.html`
- `reset_password.html`

---

## Making required imports

Head to your `views.py` file and import the following:
```python
from django.shortcuts import render, redirect  
from django.contrib.auth.models import User  
from django.contrib.auth import authenticate, login, logout  
from django.contrib.auth.decorators import login_required  
from django.contrib import messages  
from django.conf import settings  
from django.core.mail import EmailMessage  
from django.utils import timezone  
from django.urls import reverse  
from .models import *  
```

---

## Create superuser
```bash
python manage.py createsuperuser
```
- Login to admin Dashboard with credentials: `127.0.0.1:8000/admin`

---

## Creating Home, Register and Login views

### Home view
```python
def home(request):
    return render(request, 'index.html')
```

### Register views
```python
def registerview(request):
    return render(request, 'register.html')

def loginview(request):
    return render(request, 'login.html')
```

### Map views to URLs
```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.registerview, name='register'),
    path('login/', views.loginview, name='login'),
    path('logout/', views.logoutview, name='logout'),
]
```

---

## Working on Register View

- Change static file links in all files
```html
<link rel="stylesheet" href="{% static 'style.css' %}">
```

- In `register.html`, give input fields a `name` attribute & add `{% csrf_token %}`

- In `registerview`, check for incoming form submission and grab user data
```python
if request.method == 'POST':
    first_name = request.POST.get('first_name')
    last_name = request.POST.get('last_name')
    username = request.POST.get('username')
    email = request.POST.get('email')
    password = request.POST.get('password')
```

- Validate the data provided
```python
user_data_has_error = False

if User.objects.filter(username=username).exists():
    user_data_has_error = True
    messages.error(request, 'Username already exists')

if User.objects.filter(email=email).exists():
    user_data_has_error = True
    messages.error(request, 'Email already exists')

if len(password) < 6:
    user_data_has_error = True
    messages.error(request, 'Password must be at least 6 characters long')

if user_data_has_error:
    return redirect('register')
```

- Create a new user if there are no errors
```python
new_user = User.objects.create_user(
    first_name=first_name,
    last_name=last_name,
    username=username,
    email=email,
    password=password
)
messages.success(request, 'Account created successfully. Login now.')
return redirect('login')
```

---

## Display incoming messages in templates

```html
{% if messages %}
    {% for message in messages %}
        {% if message.tags == 'error' %}
            <center><h4 style="color: firebrick;">{{message}}</h4></center>
        {% else %}
            <center><h4 style="color: dodgerblue;">{{message}}</h4></center>
        {% endif %}
    {% endfor %}
{% endif %}
```

---

## Working on Login View

- In `login.html`, give input fields a `name` attribute & add `{% csrf_token %}`

- In `loginview`, check for incoming form submission and authenticate user
```python
if request.method == 'POST':
    username = request.POST.get('username')
    password = request.POST.get('password')
    
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return redirect('home')
    else:
        messages.error(request, 'Invalid login credentials')
        return redirect('login')
```

- Restrict access to home page to authenticated users
```python
@login_required
def Home(request):
    return render(request, 'index.html')
```

- Set `LOGIN_URL` in `settings.py`
```python
LOGIN_URL = 'login'
```

---

## Logout View
```python
def LogoutView(request):
    logout(request)
    return redirect('login')
```

Map view:
```python
path('logout/', views.logoutview, name='logout')
```

---

## Forgot Password

- Create views:
```python
def ForgotPassword(request):
    return render(request, 'forgot_password.html')

def PasswordResetSent(request, reset_id):
    return render(request, 'password_reset_sent.html')

def ResetPassword(request, reset_id):
    return render(request, 'reset_password.html')
```

Map the views:
```python
path('password-forgot/', views.forgotpassword , name='password-forgot'),
path('password-reset-sent/<str:reset_id>/', views.passwordresetsent, name='password-reset-sent'),
path('reset-password/<str:reset_id>/', views.passwordreset, name='reset_password'),
```

---

## Password Reset Model
```python
from django.db import models
from django.conf import settings
import uuid

class PasswordReset(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"
```

```bash
python manage.py makemigrations
python manage.py migrate
```

- Register model in admin
```python
from .models import *

admin.site.register(PasswordReset)
```

---

## Forgot Password View

- `forgot_password.html` example:
```html
<input type="email" required name="email">
```

- Check for incoming form submission:
```python
if request.method == 'POST':
    email = request.POST.get('email')
    
    try:
        user = User.objects.get(email=email)
        new_password_reset = PasswordReset(user=user)
        new_password_reset.save()
        
        password_reset_url = reverse('reset-password', kwargs={'reset_id': new_password_reset.reset_id})
        email_body = f'Reset your password using the link below:\n\n\n{password_reset_url}'
        
        email_message = EmailMessage(
            'Reset your password',
            email_body,
            settings.EMAIL_HOST_USER,
            [email]
        )
        email_message.fail_silently = True
        email_message.send()
        
        return redirect('password-reset-sent')
    
    except User.DoesNotExist:
        messages.error(request, f"No user with email '{email}' found")
        return redirect('forgot-password')
```

---

## Setup Email Settings for Password Reset

To send password reset emails, configure the email settings in `settings.py`:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_HOST_USER = "your_email@gmail.com"
EMAIL_HOST_PASSWORD = "your_google_app_password"
```

> **Important:** For Gmail users, you need to create an **App Password** to allow Django to send emails.  
> Follow this link to generate your app password:  
> [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

---

## Password Reset Sent View
```python
def PasswordResetSent(request, reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')
```

---

## Password Reset View
```python
def ResetPassword(request, reset_id):
    try:
        reset_id = PasswordReset.objects.get(reset_id=reset_id)
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid reset id')
        return redirect('forgot-password')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        passwords_have_error = False

        if password != confirm_password:
            passwords_have_error = True
            messages.error(request, 'Passwords do not match')

        if len(password) < 5:
            passwords_have_error = True
            messages.error(request, 'Password must be at least 5 characters long')

        expiration_time = reset_id.created_when + timezone.timedelta(minutes=10)
        if timezone.now() > expiration_time:
            reset_id.delete()
            passwords_have_error = True
            messages.error(request, 'Reset link has expired')

        if not passwords_have_error:
            user = reset_id.user
            user.set_password(password)
            user.save()
            reset_id.delete()
            messages.success(request, 'Password reset. Proceed to login')
            return redirect('login')
        else:
            return redirect('reset-password', reset_id=reset_id)

    return render(request, 'reset_password.html')
```

---

## Test The Code

- Ensure that users can register, login, logout, and reset passwords successfully.
- Prevent authenticated users from visiting authentication pages.
