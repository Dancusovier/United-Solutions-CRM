from django.db import models


class Client(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)
    ssn_last4 = models.CharField(max_length=4, blank=True, null=True)

    qualification_notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Lead(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('converted', 'Converted'),
        ('archived', 'Archived'),
    ]

    client = models.OneToOneField(
        Client,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Linked client after conversion"
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    date_of_birth = models.DateField(blank=True, null=True)
    ssn_last4 = models.CharField(max_length=4, blank=True, null=True)

    qualification_notes = models.TextField(blank=True, null=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )


    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def convert_to_client(self):
        client, _ = Client.objects.get_or_create(
            email=self.email,
            defaults={
                'first_name': self.first_name,
                'last_name': self.last_name,
                'phone': self.phone,
            }
        )
        self.client = client
        self.status = 'converted'
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"


class Interaction(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='lead_interactions'
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='client_interactions'
    )
    note = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.note[:30]}"
