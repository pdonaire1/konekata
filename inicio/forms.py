# -*- coding: utf-8 -*-
from django import forms
#Formulario de login
class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'usuario'}))
    password = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Password'}))
    
    
class RecuperarPassForm(forms.Form):
    correo = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'correo electrónico'}))
    
    
class CambiarPasswordForm(forms.Form):
    password = forms.CharField(label='Contraseña Actual', widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Contraseña'}))
    password_uno = forms.CharField(label='Contraseña Nueva',widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Contraseña Nueva'}))
    password_dos = forms.CharField(label='Repetir Contraseña Nueva',widget=forms.PasswordInput(render_value=False, attrs={'placeholder': 'Contraseña Nueva'}))
    