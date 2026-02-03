from django.shortcuts import render, get_object_or_404, redirect
from .models import Client, TotalPayments


def sales_made_list(request):
    clients = Client.objects.filter(sales_made=True)
    total, _ = TotalPayments.objects.get_or_create(id=1)

    return render(request, 'core/sales_made_list.html', {
        'clients': clients,
        'total': total
    })


def confirm_add_payment(request, client_id):
    client = get_object_or_404(Client, id=client_id)

    if request.method == "POST":
        total, _ = TotalPayments.objects.get_or_create(id=1)
        total.total_amount += client.payment_amount
        total.save()
        return redirect('sales_made_list')

    return render(request, 'core/confirm_add_payment.html', {
        'client': client
    })
