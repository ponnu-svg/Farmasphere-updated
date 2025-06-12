from django.apps import AppConfig


class SignuploginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'signupLogin'
class YourAppNameConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'signupLogin'

    def ready(self):
        import signupLogin.signals  
