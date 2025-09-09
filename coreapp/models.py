from django.db import models
from django.conf import settings  # ✅ à utiliser pour référencer l'utilisateur
import uuid


class PasswordReset(models.Model):   # ✅ Class → class, convention : PascalCase
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reset_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_when = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_when}"

