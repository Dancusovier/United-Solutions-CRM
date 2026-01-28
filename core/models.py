from django.db import models


# ---------------------------
# Completed Clients / Sales Made
# ---------------------------
class SalesMade(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Address info
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    # Personal info
    date_of_birth = models.DateField(blank=True, null=True)
    ssn_last4 = models.CharField("SSN (/Last 4)", max_length=9, blank=True, null=True)

    # Notes & services
    qualification_notes = models.TextField(blank=True, null=True)
    service_1_selected = models.BooleanField(default=False)
    service_1_info = models.TextField(blank=True, null=True)
    service_2_selected = models.BooleanField(default=False)
    service_2_info = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Sales Made"
        verbose_name_plural = "Sales Made"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# ---------------------------
# Prospective Clients
# ---------------------------
class Client(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('converted', 'Converted'),
        ('archived', 'Archived'),
    ]

    # Link to completed client once converted
    sales_made = models.OneToOneField(
        SalesMade,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Linked Sales Made client after conversion"
    )

    # Basic info
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    source = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # Address info
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    zip_code = models.CharField(max_length=10, blank=True, null=True)

    # Personal info
    date_of_birth = models.DateField(blank=True, null=True)
    ssn_last4 = models.CharField("SSN (/Last 4)", max_length=9, blank=True, null=True)

    # Notes & services
    qualification_notes = models.TextField(blank=True, null=True)
    service_1_selected = models.BooleanField(default=False)
    service_1_info = models.TextField(blank=True, null=True)
    service_2_selected = models.BooleanField(default=False)
    service_2_info = models.TextField(blank=True, null=True)

    # Status
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    # ---------------------------
    # Convert prospective client to completed sales
    # ---------------------------
    def convert_to_sales_made(self):
        sales_client, _ = SalesMade.objects.get_or_create(
            email=self.email,
            defaults={
                'first_name': self.first_name,
                'last_name': self.last_name,
                'phone': self.phone,
                'address': self.address,
                'city': self.city,
                'state': self.state,
                'zip_code': self.zip_code,
                'date_of_birth': self.date_of_birth,
                'ssn_last4': self.ssn_last4,
                'qualification_notes': self.qualification_notes,
                'service_1_selected': self.service_1_selected,
                'service_1_info': self.service_1_info,
                'service_2_selected': self.service_2_selected,
                'service_2_info': self.service_2_info,
            }
        )
        self.sales_made = sales_client
        self.status = 'converted'
        self.save()

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"


# ---------------------------
# Interactions
# ---------------------------
class Interaction(models.Model):
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='client_interactions'
    )
    sales_made = models.ForeignKey(
        SalesMade,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='sales_interactions'
    )
    note = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.date.strftime('%Y-%m-%d')} - {self.note[:30]}"

