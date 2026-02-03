from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from .models import Client, SalesMade, Interaction, TotalPayments
from django.template.response import TemplateResponse
from django.utils.html import format_html

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
            ('Sensitive Info', {'fields': ('date_of_birth', 'ssn_last4', 'mother_maiden_name')}),
            ('Qualification', {'fields': ('qualification_notes',)}),
            ('Service & Payment', {
                'fields': (
                    'service_description',
                    'payment_amount',
                    'payment_date',
                    'cardholder_name',
                    'card_type',
                    'card_number',
                    'card_expiration',
                    'card_cvv' ,
                )
            }),

        ]



        return fieldsets

# ---------------------------
# SalesMade Admin
# ---------------------------
@admin.register(SalesMade)
class SalesMadeAdmin(admin.ModelAdmin):
    form = DOBAdminForm
    list_display = ('first_name', 'last_name', 'email', 'phone', 'add_payment_button')
    search_fields = ('first_name', 'last_name', 'email', 'phone')

    def total_payments_counter(self, request):
        from .models import TotalPayments
        total = TotalPayments.objects.first()
        return total.total_amount if total else 0

    inlines = [SalesInteractionInline]

    actions = ['add_payment_to_total']

    def add_payment_to_total(self, request, queryset):
        total, _ = TotalPayments.objects.get_or_create(id=1)

        for sale in queryset:
            if sale.payment_amount:
                total.total_amount += sale.payment_amount

        total.save()
        self.message_user(request, "Selected payments were added to the total.")

    add_payment_to_total.short_description = "Add selected payments to total counter"

    # Mirror the same layout as ClientAdmin
    def get_fieldsets(self, request, obj=None):
        fieldsets = [
            ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone')}),
            ('Address', {'fields': ('address', 'city', 'state', 'zip_code')}),
            ('Sensitive Info', {'fields': ('date_of_birth', 'ssn_last4', 'mother_maiden_name')}),
            ('Qualification', {'fields': ('qualification_notes',)}),
            ('Service & Payment', {
                'fields': (
                    'service_description',
                    'payment_amount',
                    'payment_date',
                    'cardholder_name',
                    'card_type',
                    'card_number',
                    'card_expiration',
                    'card_cvv',
                )
            }),
        ]
        return fieldsets

    # <-- ADD THIS METHOD HERE
    def changelist_view(self, request, extra_context=None):
        from .models import TotalPayments
        total, _ = TotalPayments.objects.get_or_create(id=1)
        extra_context = extra_context or {}
        extra_context['total_payments'] = total
        return super().changelist_view(request, extra_context=extra_context)

    # <-- KEEP THIS AT THE VERY BOTTOM
    change_list_template = "admin/salesmade_change_list.html"

    def add_payment_button(self, obj):
        return format_html(
            '<a class="button" href="/admin/core/salesmade/{}/change/">Add Payment</a>',
            obj.id
        )

    add_payment_button.short_description = "Actions"