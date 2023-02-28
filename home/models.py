from django.db import models
from django.contrib.auth.models import User
import uuid

class UserUuid(models.Model):
    uuid = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_uuid')

    def __str__(self) -> str:
        return str(self.uuid)