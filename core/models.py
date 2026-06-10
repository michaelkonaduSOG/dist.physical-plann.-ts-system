from django.db import models
from django.conf import settings


def format_ghana_card(raw):
    raw = ''.join(filter(str.isdigit, str(raw)))

    if len(raw) != 10:
        return raw

    return f"GHA-{raw[:9]}-{raw[9]}"


class Structure(models.Model):

    TOWN_CHOICES = [
        ("Nsuta", "Nsuta"),
        ("Beposo", "Beposo"),
        ("Kwamang", "Kwamang"),
        ("Jeduako", "Jeduako"),
        ("Bonkrong", "Bonkrong"),
        ("Amoamang", "Amoamang"),
        ("Kyebi", "Kyebi"),
        ("Atonsu", "Atonsu"),
        ("Birem", "Birem"),
        ("Kyeiase", "Kyeiase"),
    ]

    STRUCTURE_CHOICES = [
        ("Container Shop", "Container Shop"),
        ("Wooden Kiosk", "Wooden Kiosk"),
        ("Metal Kiosk", "Metal Kiosk"),
        ("Food Stall", "Food Stall"),
        ("Canopy", "Canopy"),
        ("Temporary Shed", "Temporary Shed"),
        ("Other", "Other"),
    ]

    PERMIT_CHOICES = [
        ("PAID", "Paid"),
        ("ARREARS", "Arrears"),
        ("NOT_REGISTERED", "Not Registered"),
    ]

    # TS ID
    ts_id = models.CharField(max_length=10, unique=True, blank=True)

    # Owner
    owner_name = models.CharField(max_length=200)
    owner_phone = models.CharField(max_length=20)
    ghana_card = models.CharField(max_length=20)

    # Location
    town = models.CharField(max_length=50, choices=TOWN_CHOICES)
    area = models.CharField(max_length=200)
    latitude = models.FloatField()
    longitude = models.FloatField()

    # Structure
    structure_type = models.CharField(max_length=50, choices=STRUCTURE_CHOICES)
    permit_status = models.CharField(max_length=20, choices=PERMIT_CHOICES)

    # Evidence
    evidence_photo = models.ImageField(upload_to="evidence_photos/")

    # Notes
    notes = models.TextField(blank=True)

    # Collector
    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="structures"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):

        # Ghana card formatting
        if self.ghana_card and not self.ghana_card.startswith("GHA"):
            self.ghana_card = format_ghana_card(self.ghana_card)

        # TS ID generation
        if not self.ts_id:
            last = Structure.objects.order_by('-id').first()

            if last and last.ts_id:
                try:
                    last_num = int(last.ts_id.replace("TS", ""))
                    new_num = last_num + 1
                except:
                    new_num = 1
            else:
                new_num = 1

            self.ts_id = f"TS{new_num:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.ts_id} - {self.owner_name}"
class PaymentHistory(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    structure = models.ForeignKey(
        "Structure",
        on_delete=models.CASCADE,
        related_name="payments"
    )

    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments"
    )

    receipt_photo = models.ImageField(upload_to="receipts/")

    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    admin_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.structure.ts_id} - {self.status}"
    

class EditRequest(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
    ]

    structure = models.ForeignKey(
        "Structure",
        on_delete=models.CASCADE,
        related_name="edit_requests"
    )

    collector = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="edit_requests"
    )

    field_name = models.CharField(max_length=50)

    old_value = models.TextField()

    new_value = models.TextField()

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    admin_comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.structure.ts_id} - {self.field_name}"