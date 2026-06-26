from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Менеджер пользователей"""

    def create_user(self, email, name,
                    surname, phone, password=None, **extra_fields):
        """Создание обычного пользователя"""
        if not email:
            raise ValueError('Email обязателен для заполнения')
        if not name:
            raise ValueError('Имя обязательно для заполнения')
        if not surname:
            raise ValueError('Фамилия обязательна для заполнения')
        if not phone:
            raise ValueError('Телефон обязателен для заполнения')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name,
            surname=surname,
            phone=phone,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname,
                         phone, password=None, **extra_fields):
        """Создание суперпользователя"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            text = 'Суперпользователь должен иметь is_staff=True'
            raise ValueError(text)
        if extra_fields.get('is_superuser') is not True:
            text = 'Суперпользователь должен иметь is_superuser=True'
            raise ValueError(text)

        return self.create_user(email, name, surname,
                                phone, password, **extra_fields)
