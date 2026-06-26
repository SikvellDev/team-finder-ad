import re

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import PasswordChangeForm
from django.core.exceptions import ValidationError
from django.db import models

from core.mixins import GitHubURLMixin
from users.constants import ABOUT_ROWS, PASSWORD_MIN_LENGTH

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    """Форма регистрации нового пользователя"""

    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )

    class Meta:
        model = User
        fields = ['name', 'surname', 'email', 'password']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'example@mail.com'
            }),
        }
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'email': 'Email',
        }

    def clean_email(self):
        """Проверка уникальности email"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            text = 'Пользователь с таким email уже существует'
            raise forms.ValidationError(text)
        return email

    def save(self, commit=True):
        """Сохраняем пользователя с хэшированным паролем"""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    """Форма авторизации пользователя"""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'example@mail.com'
        }),
        label='Email',
        error_messages={
            'required': 'Введите email',
            'invalid': 'Введите корректный email'
        }
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        }),
        label='Пароль',
        min_length=PASSWORD_MIN_LENGTH,
        error_messages={
            'required': 'Введите пароль',
            'min_length': 'Пароль должен содержать минимум 6 символов'
        }
    )


class ProfileEditForm(GitHubURLMixin, forms.ModelForm):
    """Форма редактирования профиля пользователя"""

    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя'
            }),
            'surname': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите фамилию'
            }),
            'about': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Расскажите о себе',
                'rows': ABOUT_ROWS
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+7 999 123-45-67'
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }
        help_texts = {
            'avatar': 'Загрузите изображение для аватара (JPG, PNG)',
            'phone': 'Форматы: 8XXXXXXXXXX или +7XXXXXXXXXX',
            'github_url': 'Ссылка на ваш GitHub профиль',
        }

    def clean_phone(self):
        """Валидация и нормализация номера телефона"""
        phone = self.cleaned_data.get('phone')

        if not phone:
            return phone

        phone = re.sub(r'[\s\-\(\)\.]', '', phone)

        pattern_8 = r'^8\d{10}$'
        pattern_7 = r'^\+7\d{10}$'

        if re.match(pattern_8, phone):
            phone = '+7' + phone[1:]
        elif re.match(pattern_7, phone):
            pass
        else:
            text = ('Неверный формат телефона.' +
                    'Используйте 8XXXXXXXXXX или +7XXXXXXXXXX (X - цифры)')
            raise ValidationError(text)

        user_id = self.instance.pk if self.instance else None
        phone_with_8 = '8' + phone[2:]
        phone_with_7 = phone

        if User.objects.exclude(pk=user_id).filter(
            models.Q(phone=phone_with_7) | models.Q(phone=phone_with_8)
        ).exists():
            text = 'Пользователь с таким номером телефона уже существует'
            raise ValidationError(text)

        return phone

    def clean_avatar(self):
        """Валидация аватара"""
        avatar = self.cleaned_data.get('avatar')

        if avatar:
            if avatar.size > 5 * 1024 * 1024:
                raise ValidationError('Размер аватара не должен превышать 5MB')

            file_name = avatar.name.lower()
            valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp']
            is_valid_extension = any(
                file_name.endswith(ext) for ext in valid_extensions
            )

            try:
                content_type = avatar.content_type
                is_valid_content_type = content_type.startswith('image/')
            except AttributeError:
                is_valid_content_type = is_valid_extension

            if not is_valid_extension and not is_valid_content_type:
                text = 'Загрузите изображение (JPG, PNG, GIF, BMP)'
                raise ValidationError(text)

        return avatar


class PasswordChangeForm(PasswordChangeForm):
    """Форма смены пароля"""

    old_password = forms.CharField(
        label='Старый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите старый пароль'
        })
    )

    new_password1 = forms.CharField(
        label='Новый пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите новый пароль'
        }),
        help_text='Пароль должен содержать минимум 6 символов'
    )

    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Подтвердите новый пароль'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        text = 'Пароль должен содержать минимум 6 символов'
        self.fields['new_password1'].help_text = text
