from django.apps import AppConfig

class SplitappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'splitApp'

    # def ready(self):
    #     from .models import Expense
    #     from django.contrib.auth.models import Permission
    #     from django.contrib.contenttypes.models import ContentType
    #     content_type = ContentType.objects.get_for_model(Expense)
    #     permission, created = Permission.objects.get_or_create(
    #         codename='can_create_expense',
    #         name='Can create expense',
    #         content_type=content_type,
    #     )

    #     if created:
    #         print('Successfully created permission "can_create_expense"')
    #     else:
    #         print('Permission "can_create_expense" already exists')