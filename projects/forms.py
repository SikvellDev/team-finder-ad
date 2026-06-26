from django import forms

from projects.models import Project
from validators import validate_github_url


class ProjectForm(forms.ModelForm):
    """Форма создания и редактирования проекта"""

    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название проекта'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Опишите цели и задачи проекта',
                'rows': 5
            }),
            'github_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://github.com/username/repository'
            }),
            'status': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
        help_texts = {
            'github_url': 'Ссылка на GitHub репозиторий (если есть)',
            'status': ('Открытый - проект ищет участников,' +
                       'Закрытый - набор завершён'),
        }
        error_messages = {
            'name': {
                'required': 'Название проекта обязательно',
                'max_length': 'Название не может быть длиннее 200 символов',
            },
        }

    def clean_github_url(self):
        """Валидация GitHub URL"""
        github_url = self.cleaned_data.get('github_url')
        return validate_github_url(github_url)
