from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Client, SalesMade, Interaction
from django.template.response import TemplateResponse

# ---------------------------
# Interaction Inlines
# ---------------------------
class ClientInteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    exclude = ('sales_made',)  # hide completed client field for prospective client interactions

class SalesInteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    exclude = ('client',)  # hide prospective client field for sales interactions

# ---------------------------
# Date of Birth Widget
# ---------------------------
class DOBAdminForm(forms.ModelForm):
    date_of_birth = forms.DateField(
        widget=forms.DateInput(format='%m-%d-%Y'),
        input_formats=['%m-%d-%Y'],
        required=False,
    )

    class Meta:
        model = Client
        fields = '__all__'

# ---------------------------
# Client Admin
# ---------------------------
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    form = DOBAdminForm
    list_display = ('first_name', 'last_name', 'email', 'status')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    inlines = [ClientInteractionInline]
    actions = ['convert_selected_clients']

    # -----------------------
    # Convert selected clients to SalesMade
    # -----------------------
    def convert_selected_clients(self, request, queryset):
        for client in queryset.filter(status='active'):
            client.convert_to_sales_made()
        self.message_user(request, "Selected clients were converted to Sales Made.")
    convert_selected_clients.short_description = "Convert selected clients to Sales Made"

    # -----------------------
    # Only show active clients
    # -----------------------
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status__in=['converted', 'archived'])

    # -----------------------
    # Field layout with conditional service info
    # -----------------------
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
            ('Address', {'fields': ('address', 'city', 'state', 'zip_code')}),
            ('Sensitive Info', {'fields': ('date_of_birth', 'ssn_last4')}),
            ('Qualification', {'fields': ('qualification_notes',)}),
            ('Services', {'fields': ('service_1_selected', 'service_2_selected')}),
        ]

        if obj:
            service_fields = []
            if obj.service_1_selected:
                service_fields.append('service_1_info')
            if obj.service_2_selected:
                service_fields.append('service_2_info')
            if service_fields:
                fieldsets.append(('Service Details', {'fields': service_fields}))

        return fieldsets

# ---------------------------
# SalesMade Admin
# ---------------------------
@admin.register(SalesMade)
class SalesMadeAdmin(admin.ModelAdmin):
    form = DOBAdminForm
    list_display = ('first_name', 'last_name', 'email', 'phone')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    inlines = [SalesInteractionInline]

    # Mirror the same layout as ClientAdmin
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
            ('Address', {'fields': ('address', 'city', 'state', 'zip_code')}),
            ('Sensitive Info', {'fields': ('date_of_birth', 'ssn_last4')}),
            ('Qualification', {'fields': ('qualification_notes',)}),
            ('Services', {'fields': ('service_1_selected', 'service_2_selected')}),
        ]

        if obj:
            service_fields = []
            if obj.service_1_selected:
                service_fields.append('service_1_info')
            if obj.service_2_selected:
                service_fields.append('service_2_info')
            if service_fields:
                fieldsets.append(('Service Details', {'fields': service_fields}))

        return fieldsets
