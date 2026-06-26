import uuid
from io import BytesIO

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont

from users.constants import (AVATAR_SIZE, COLOR_WHITE, COLORS, FONT_PATHS,
                             PHONE_MAX_LENGTH, SKILL_NAME_MAX_LENGTH,
                             USER_ABOUT_MAX_LENGTH, USER_NAME_MAX_LENGTH,
                             USER_SURNAME_MAX_LENGTH)
from users.managers import UserManager


class Skill(models.Model):
    """Модель навыков пользователя"""

    name = models.CharField(
        max_length=SKILL_NAME_MAX_LENGTH,
        unique=True,
        verbose_name='Название навыка'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """Модель пользователя"""

    email = models.EmailField(
        unique=True,
        verbose_name='Адрес электронной почты',
        error_messages={
            'unique': 'Пользователь с таким email уже существует',
        }
    )
    name = models.CharField(
        max_length=USER_NAME_MAX_LENGTH,
        verbose_name='Имя'
    )
    surname = models.CharField(
        max_length=USER_SURNAME_MAX_LENGTH,
        verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        verbose_name='Аватар'
    )
    phone = models.CharField(
        max_length=PHONE_MAX_LENGTH,
        verbose_name='Телефон'
    )
    github_url = models.URLField(
        blank=True,
        verbose_name='GitHub'
    )
    about = models.TextField(
        max_length=USER_ABOUT_MAX_LENGTH,
        blank=True,
        verbose_name='О себе'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активный пользователь'
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name='Администратор'
    )
    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name='users',
        verbose_name='Навыки'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname', 'phone']

    objects = UserManager()

    class Meta:
        ordering = ['-id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.name} {self.surname}'
    
    def save(self, *args, **kwargs):
        """Переопределение save для автоматической генерации аватарки"""
        is_new = not self.pk

        if is_new or not self.avatar:
            super().save(*args, **kwargs)
            self._generate_avatar()
            super().save(update_fields=['avatar'])
        else:
            super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def _generate_avatar(self):
        """Генерация аватарки с первой буквой имени на однотонном фоне"""
        letter = self.name[0].upper() if self.name else '?'

        color_index = hash(self.name) % len(COLORS)
        bg_color = COLORS[color_index]

        image = Image.new('RGB', (AVATAR_SIZE, AVATAR_SIZE), bg_color)
        draw = ImageDraw.Draw(image)

        font = None
        font_size = int(AVATAR_SIZE * 0.6)

        for path in FONT_PATHS:
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except (IOError, OSError):
                continue

        if font is None:
            font = ImageFont.load_default(size=font_size)

        try:
            bbox = draw.textbbox((0, 0), letter, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = (AVATAR_SIZE - text_width) // 2 - bbox[0]
            y = (AVATAR_SIZE - text_height) // 2 - bbox[1]
        except AttributeError:
            text_width, text_height = draw.textsize(letter, font=font)
            x = (AVATAR_SIZE - text_width) // 2
            y = (AVATAR_SIZE - text_height) // 2

        draw.text((x, y), letter, fill=COLOR_WHITE, font=font)

        buffer = BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)

        filename = f'avatar_{uuid.uuid4().hex}.png'
        self.avatar.save(filename, ContentFile(buffer.read()), save=False)
        buffer.close()
