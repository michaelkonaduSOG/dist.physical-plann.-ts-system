from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string


def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))


class User(AbstractUser):

    phone = models.CharField(max_length=20, unique=True)
    collector_id = models.CharField(max_length=10, unique=True, blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=[('ADMIN', 'Admin'), ('COLLECTOR', 'Collector')],
        default='COLLECTOR'
    )

    must_change_password = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        creating = self.pk is None

        # 🚨 ONLY FORCE COLLECTOR RULE IF NOT ADMIN
        if self.role == 'COLLECTOR':
            self.is_staff = False
            self.is_superuser = False

            # AUTO SC ID
            if not self.collector_id:
                last = User.objects.filter(role='COLLECTOR').order_by('-id').first()

                if last and last.collector_id:
                    try:
                        num = int(last.collector_id.replace("SC", ""))
                        self.collector_id = f"SC{num + 1:03d}"
                    except:
                        self.collector_id = "SC001"
                else:
                    self.collector_id = "SC001"

            # AUTO PASSWORD
            if creating:
                raw = generate_password()
                self.set_password(raw)
                self._raw_password = raw
                self.must_change_password = True

        super().save(*args, **kwargs)