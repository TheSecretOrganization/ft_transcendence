from django.apps import AppConfig


class FtAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ft_auth'

    def ready(self) -> None:
        from . import oauth
        return super().ready()