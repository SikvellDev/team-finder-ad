# validators.py
import re

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


def validate_github_url(value):
    """Валидатор для проверки, что URL ведет на GitHub"""
    if not value:
        return value
    
    # Проверка на валидный URL
    url_validator = URLValidator()
    try:
        url_validator(value)
    except ValidationError:
        raise ValidationError('Введите корректный URL')
    
    # Проверка, что это GitHub URL
    github_patterns = [
        r'^https?://github\.com/',
        r'^https?://www\.github\.com/',
    ]
    
    is_github = any(
        re.match(pattern, value, re.IGNORECASE) 
        for pattern in github_patterns
    )
    
    if not is_github:
        raise ValidationError(
            'Ссылка должна вести на GitHub (https://github.com/username)'
        )
    
    return value
