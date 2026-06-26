from core.validators import validate_github_url


class GitHubURLMixin:
    """Миксин для валидации GitHub URL в формах"""

    def clean_github_url(self):
        """Валидация GitHub URL"""
        github_url = self.cleaned_data.get('github_url')

        if not github_url:
            return github_url

        return validate_github_url(github_url)
