from resources.models import User


class ManagedUser(User):
    class Meta:
        proxy = True
        verbose_name = "User"
        verbose_name_plural = "Users"
