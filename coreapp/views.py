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

# Page d'accueil
@login_required 
def home(request):
    return render(request, 'index.html')


# Inscription
def registerview(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_data_has_error = False

        # Vérification des doublons
        if User.objects.filter(username=username).exists():
            user_data_has_error = True
            messages.error(request, 'Username already exists')

        if User.objects.filter(email=email).exists():
            user_data_has_error = True
            messages.error(request, 'Email already exists')

        # Vérification du mot de passe
        if len(password) < 6:
            user_data_has_error = True
            messages.error(request, 'Password must be at least 6 characters long')

        # Si erreur -> retour au formulaire
        if user_data_has_error:
            return redirect('register')

        # Sinon, créer l'utilisateur
        new_user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        messages.success(request, 'Account created successfully. Login now.')
        return redirect('login')

    return render(request, 'register.html')


# Connexion
def loginview(request):
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
    return render(request, 'login.html')


# Déconnexion                   
def logoutview(request):
    logout(request)
    return redirect('login')

# Mot de passe oublié
def forgotpassword(request):
    if request.method == 'POST':
        email = request.POST.get('email')

        try:
            user = User.objects.get(email=email)
            
            new_password_reset = PasswordReset.objects.create(user=user)
            new_password_reset.save()
            
            password_reset_url = reverse('reset_password', kwargs={'reset_id': new_password_reset.reset_id})
            full_password_reset_url = f"{request.scheme}://{request.get_host()}{password_reset_url}"

            email_body = f"Click the link below to reset your password:\n\n {full_password_reset_url}\n\nIf you did not request this, please ignore this email."
            
            email_message = EmailMessage(
                subject="Password Reset Request",
                body=email_body,
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email], 
            )
            
            email_message.send(fail_silently=False)
            email_message.send()
            
            return redirect('password-reset-sent', reset_id=new_password_reset.reset_id)    
            
        except User.DoesNotExist:
            messages.error(request, f"No user is associated with this email address: {email}")
            
            return redirect('password-forgot')
    return render(request, 'forgot_password.html')



# Confirmation de réinitialisation
def passwordresetsent(request ,reset_id):
    if PasswordReset.objects.filter(reset_id=reset_id).exists():
        return render(request, 'password_reset_sent.html')
    else:
        messages.error(request, 'Invalid password reset link.')
        return redirect('password-forgot')
    return render(request, 'password_reset_sent.html')


# Réinitialisation du mot de passe
def passwordreset(request, reset_id):
    try:
        password_reset_id = PasswordReset.objects.get(reset_id=reset_id)
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            password_have_error = False         
            if password != confirm_password:
                password_have_error = True
                messages.error(request, 'Passwords do not match.')
            
            if len(password) < 6:
                password_have_error = True
                messages.error(request, 'Password must be at least 6 characters long.')
                
            expiration_time = password_reset_id.created_when + timezone.timedelta(minutes=10)
            
            if timezone.now() > expiration_time:
                password_have_error = True
                messages.error(request, 'This password reset link has expired.')
                
                password_reset_id.delete()
            
            if not password_have_error:
                user = password_reset_id.user
                user.set_password(password)
                user.save()
                password_reset_id.delete()
            
                messages.success(request, 'Password has been reset successfully. You can now log in with your new password.')
                return redirect('login') 
            else:
                return redirect('reset_password', reset_id=reset_id) 
        
        
    except PasswordReset.DoesNotExist:
        messages.error(request, 'Invalid password reset link.')
        return redirect('password-forgot')
    
    return render(request, 'reset_password.html')

