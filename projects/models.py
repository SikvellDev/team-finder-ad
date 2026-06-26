from django.conf import settings
from django.db import models

from projects.constants import NAME_PROJECT_MAX_LENGTH


class Project(models.Model):
    """Модель проекта"""

    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    name = models.CharField(
        max_length=NAME_PROJECT_MAX_LENGTH,
        verbose_name='Название проекта',
    )
    description = models.CharField(
        blank=True,
        verbose_name='Описание проекта',
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Автор проекта',
        related_name='owned_projects',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )
    github_url = models.URLField(
        blank=True,
        verbose_name='Ссылка на Github',
    )
    status = models.CharField(
        max_length=6,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='Статус проекта',
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
        verbose_name='Участники проекта'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return self.name

    @property
    def is_open(self):
        """Проверка, открыт ли проект для участников"""
        return self.status == self.Status.OPEN

    def close_project(self):
        """Закрыть проект"""
        self.status = self.Status.CLOSED
        self.save()

    def open_project(self):
        """Открыть проект"""
        self.status = self.Status.OPEN
        self.save()

    def get_participants_count(self):
        """Количество участников проекта"""
        return self.participants.count()

    def is_participant(self, user):
        """Проверка, участвует ли пользователь в проекте"""
        if not user or not user.is_authenticated:
            return False
        return self.participants.filter(id=user.id).exists()
