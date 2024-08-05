from django.shortcuts import render, redirect
from django.urls import reverse
from solar.invoice_generator.Bill_Reader import bill_reader
from solar.invoice_generator.invoicemaker import generate_invoice
from solar.models import Panel, Inverter, PotentialCustomers, variableCosts
import math
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
import json

def index(request):
    return render(request, 'solar/index.html')

def quotation(request):
    return render(request, 'solar/quotation.html')

def generate_invoice_view(request):
    if request.method == 'POST':
        reference_number = request.POST.get('reference_number')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        try:
            invoice_data = bill_reader(reference_number, address)
            name = invoice_data['Name']
            panel_power = 545  # 545 watts
            potential_customer = PotentialCustomers.objects.create(name=name, address=address, phone=phone_number, reference_number=reference_number)
            potential_customer.save()
            total_power_of_1_panel = 1780 * 0.8  # 80% efficiency
            print(int(invoice_data['Total Yearly Units']))
            panels_needed = int(invoice_data['Total Yearly Units']) / total_power_of_1_panel
            print(f"Panels needed: {panels_needed}")
            panels_needed = math.ceil(panels_needed)
            print(f"Panels needed: {panels_needed}")
            system_size = math.ceil((panels_needed * panel_power)/1000)
            print(f"System size: {system_size}")
            inverter_price = 200000
            brand = 'GoodWe'
            panel_price = 20000
            net_metering = 150000
            total_cost = system_size * panel_price + inverter_price + net_metering + 200000
            #generate_invoice(system_size, panels_needed, panel_power, inverter_price, brand, panel_price, net_metering, 50000, 50000, 50000, 50000, total_cost, name, address, phone_number)
            # Process invoice_data as needed
            print(invoice_data)
            response_data = {
                'name': name,
                'address': address,
                'phone': phone_number,
                'reference_number': reference_number,
                'electricity_bill': invoice_data['Payable Within Due Date'],
                'monthly_units': invoice_data['Units Consumed'],
                'yearly_units': invoice_data['Total Yearly Units'],
                'system_size': system_size,
                'panel_brand': 'Jinko Solar',
                'panel_quantity': panels_needed,
                'panel_price': panel_price,
                'inverter_brand': brand,
                'inverter_price': inverter_price,
                'frame_cost': 200,
                'installation_cost': 200,
                'total_cost': total_cost
            }
            return JsonResponse(response_data)
        except Exception as e:
            return render(request, 'invoice_error.html', {'error_message': str(e)})

    return redirect(reverse('your_form_page_name'))

#@user_passes_test(lambda u: u.is_staff)
def control_panel(request):
    return render(request, 'solar/control_panel.html')

#@user_passes_test(lambda u: u.is_staff)
def panels(request):
    if request.method == 'GET':
        panels = Panel.objects.all().values()
        return JsonResponse(list(panels), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        panel = Panel.objects.create(
            brand=data['brand'],
            price=data['price'],
            power=data['power'],
            availability=data['availability']
        )
        return JsonResponse({'message': 'Panel added successfully!'})

#@user_passes_test(lambda u: u.is_staff)
def inverters(request):
    if request.method == 'GET':
        inverters = Inverter.objects.all().values()
        return JsonResponse(list(inverters), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        inverter = Inverter.objects.create(
            brand=data['brand'],
            price=data['price'],
            power=data['power'],
            availability=data['availability']
        )
        return JsonResponse({'message': 'Inverter added successfully!'})

#@user_passes_test(lambda u: u.is_staff)
def customers(request):
    customers = PotentialCustomers.objects.all().values()
    return JsonResponse(list(customers), safe=False)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def panel_list(request):
    if request.method == 'GET':
        panels = Panel.objects.all().values()
        return JsonResponse(list(panels), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        panel = Panel.objects.create(
            brand=data['brand'],
            price=data['price'],
            power=data['power'],
            availability=data['availability']
        )
        return JsonResponse({"id": panel.id}, status=201)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def panel_detail(request, id):
    panel = get_object_or_404(Panel, id=id)
    if request.method == 'PUT':
        data = json.loads(request.body)
        panel.brand = data['brand']
        panel.price = data['price']
        panel.power = data['power']
        panel.availability = data['availability']
        panel.save()
        return JsonResponse({"id": panel.id}, status=200)
    elif request.method == 'DELETE':
        panel.delete()
        return JsonResponse({"id": id}, status=200)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def inverter_list(request):
    if request.method == 'GET':
        inverters = Inverter.objects.all().values()
        return JsonResponse(list(inverters), safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        inverter = Inverter.objects.create(
            brand=data['brand'],
            price=data['price'],
            power=data['power'],
            availability=data['availability']
        )
        return JsonResponse({"id": inverter.id}, status=201)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def inverter_detail(request, id):
    inverter = get_object_or_404(Inverter, id=id)
    if request.method == 'PUT':
        data = json.loads(request.body)
        inverter.brand = data['brand']
        inverter.price = data['price']
        inverter.power = data['power']
        inverter.availability = data['availability']
        inverter.save()
        return JsonResponse({"id": inverter.id}, status=200)
    elif request.method == 'DELETE':
        inverter.delete()
        return JsonResponse({"id": id}, status=200)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def set_prices(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        variableCosts.objects.update_or_create(
            cost_name='Frame Cost per Watt', defaults={'cost': data['pricePerWatt']}
        )
        variableCosts.objects.update_or_create(
            cost_name='Installation Cost per Watt', defaults={'cost': data['installationCost']}
        )
        return JsonResponse({"status": "success"}, status=200)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def customer_list(request):
    if request.method == 'GET':
        customers = PotentialCustomers.objects.all().values()
        return JsonResponse(list(customers), safe=False)

@csrf_exempt
#@user_passes_test(lambda u: u.is_staff)
def get_prices(request):
    if request.method == 'GET':
        frame_cost = variableCosts.objects.filter(cost_name='Frame Cost per Watt').first()
        installation_cost = variableCosts.objects.filter(cost_name='Installation Cost per Watt').first()
        response_data = {
            'frame_cost_per_watt': frame_cost.cost if frame_cost else '',
            'installation_cost_per_watt': installation_cost.cost if installation_cost else '',
        }
        return JsonResponse(response_data, safe=False)
