from django.contrib import admin
from .models import Client, Lead, Interaction
from django.template.response import TemplateResponse

class LeadInteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    exclude = ('client',)


class ClientInteractionInline(admin.TabularInline):
    model = Interaction
    extra = 0
    exclude = ('lead',)



# Admin action to convert selected leads to clients
def convert_to_client(modeladmin, request, queryset):
    if 'apply' in request.POST:
        # User confirmed, do the conversion
        for lead in queryset:
            lead.convert_to_client()
        modeladmin.message_user(request, "Selected leads have been converted to clients.")
        return None
    else:
        # Show confirmation page
        context = {
            'leads': queryset,
            'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
            'queryset': queryset,
        }
        return TemplateResponse(request, "admin/convert_to_client_confirmation.html", context)
convert_to_client.short_description = "Convert selected leads to clients"

# Current registrations are still here
class ClientAdmin(admin.ModelAdmin):
    inlines = [ClientInteractionInline]

admin.site.register(Client, ClientAdmin)


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'status')
    list_filter = ('status',)
    search_fields = ('first_name', 'last_name', 'email')
    actions = ['convert_selected_leads']

    def convert_selected_leads(self, request, queryset):
        for lead in queryset.filter(status='active'):
            lead.convert_to_client()
        self.message_user(request, "Selected leads were converted to clients.")

    convert_selected_leads.short_description = "Convert selected leads to clients"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.exclude(status__in=['converted', 'archived'])





class ClientAdmin(admin.ModelAdmin):
    inlines = [ClientInteractionInline]


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(status='active')  # only show active leads


