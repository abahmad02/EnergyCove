from django.shortcuts import render, redirect
from django.urls import reverse
from solar.invoice_generator.Bill_Reader import bill_reader
from solar.invoice_generator.invoicemaker import generate_invoice
from solar.invoice_generator.bill_verify import verify_bill
from solar.invoice_generator.bill_parser_ind import parse_electricity_bill_industrial
from solar.invoice_generator.bill_parser_gen import parse_electricity_bill_general
from solar.models import Panel, Inverter, PotentialCustomers, variableCosts
import math
from django.http import JsonResponse
from django.contrib.auth.decorators import user_passes_test
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json
import requests
from bs4 import BeautifulSoup

class BillValidateAPIView(APIView):
    def post(self, request):
        # Log the incoming request data
        print(f"Request Data: {request.data}")

        reference_number = request.data.get("referenceNumber")
        if not reference_number:
            return Response({
                "status": "error",
                "message": "Reference number is required.",
                "isValid": False
            }, status=status.HTTP_400_BAD_REQUEST)

        # Call the verify_bill function to check the status
        status_result = verify_bill(reference_number)
        
        if status_result['exists']:
            print(f"Bill is valid. Source URL: {status_result.get('source_url', '')}")
            return Response({
                "status": "success",
                "message": "Bill is valid.",
                "reference_number": reference_number,
                "isValid": True,
                "source_url": status_result.get("source_url", "")
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "error",
                "message": status_result.get("message", "Bill not found."),
                "isValid": False
            }, status=status.HTTP_400_BAD_REQUEST)

class GetBillDataAPIView(APIView):
    def get(self, request, reference_number):
        if not reference_number:
            return Response({
                "status": "error",
                "message": "Reference number is required."
            }, status=status.HTTP_400_BAD_REQUEST)

        status_result = verify_bill(reference_number)
        if not status_result['exists']:
            return Response({
                "status": "error",
                "message": "Bill not found."
            }, status=status.HTTP_400_BAD_REQUEST)

        url = status_result.get("source_url")
        if not url:
            return Response({
                "status": "error",
                "message": "Valid URL not found."
            }, status=status.HTTP_400_BAD_REQUEST)

        full_url = f"{url}?refno={reference_number}"

        try:
            response = requests.get(full_url)
            response.raise_for_status()
            response.encoding = response.apparent_encoding  # Ensure proper encoding
        except requests.RequestException as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        soup = BeautifulSoup(response.text, 'html.parser')  # Use .text for decoded content
        html_content = soup.prettify()

        # Optional: clean up escape sequences
        html_content = html_content.replace("\r", "").replace("\n", "")
        #print(html_content)
        if (status_result['source_url'] == "https://bill.pitc.com.pk/mepcobill/industrial"):
            json_data = parse_electricity_bill_industrial(html_content)
        else:
            json_data = parse_electricity_bill_general(html_content)
        return Response({
            "status": "success",
            "data": json_data
        }, status=status.HTTP_200_OK)
    
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
            invoice_data = bill_reader(reference_number)
            name = invoice_data['Name']
            #panel_power = 545  # 545 watts per panel
            panel = Panel.objects.get(default_choice=True)
            panel_power = panel.power
            panel_price = panel.price
            panel_brand = panel.brand
            potential_customer = PotentialCustomers.objects.create(
                name=name, address=address, phone=phone_number, reference_number=reference_number)
            potential_customer.save()

            # Calculate recommended system size based on the customer's consumption
            daily_energy = (panel_power * 9) / 1000  # 9 hours of sunlight
            annual_energy = daily_energy * 365
            total_power_of_1_panel = float(annual_energy) * 0.8  # 80% efficiency per panel
            panels_needed = math.ceil((int(invoice_data['Max Units']) * 12) / total_power_of_1_panel)
            system_size_recommended = math.ceil((panels_needed * panel_power) / 1000)

            # Calculate sizes for smaller and larger systems
            system_size_smaller = max(system_size_recommended - 2, 1)  # Ensure at least 1kW
            system_size_larger = system_size_recommended + 2

            # Pricing calculations for all three systems
            # Find the inverter with the same power or closest to the system size
            inverters_rec = Inverter.objects.filter(power__gte=system_size_recommended).order_by('power')
            if inverters_rec.exists():
                inverter_rec = inverters_rec.first()
                print(inverter_rec)
                inverter_price_rec = inverter_rec.price
            else:
                # Handle the case when no inverter is available with the required power
                inverter_price_rec = 0
            inverters_small = Inverter.objects.filter(power__gte=system_size_smaller).order_by('power')
            if inverters_small.exists():
                inverter_small = inverters_small.first()
                print(inverter_small)
                inverter_price_small = inverter_small.price
            else:
                # Handle the case when no inverter is available with the required power
                inverter_price_small = 0
            inverters_large = Inverter.objects.filter(power__gte=system_size_larger).order_by('power')
            if inverters_large.exists():
                inverter_large = inverters_large.first()
                print(inverter_large)
                inverter_price_large = inverter_large.price
            else:
                # Handle the case when no inverter is available with the required power
                inverter_price_large = 0
            net_metering = variableCosts.objects.filter(cost_name='Net Metering').first().cost
            installation_cost_per_watt = variableCosts.objects.filter(cost_name='Installation Cost per Watt').first().cost
            frame_cost_per_watt = variableCosts.objects.filter(cost_name='Frame Cost per Watt').first().cost
            
            cabling_cost = 50000
            electrical_and_mechanical_cost = 50000
            # Total cost calculation for each system
            def calculate_total_cost(system_size, inverter_price, installation_cost, frame_cost):
                print(system_size, inverter_price, installation_cost, frame_cost)
                print(system_size * panel_price * panel_power)  
                return (system_size * panel_price * panel_power) + inverter_price + net_metering + installation_cost + frame_cost + cabling_cost + electrical_and_mechanical_cost
            
            installation_rec = system_size_recommended * installation_cost_per_watt * 1000
            installation_small = system_size_smaller * installation_cost_per_watt * 1000
            installation_large = system_size_larger * installation_cost_per_watt * 1000
            frame_cost_rec = system_size_recommended * frame_cost_per_watt * 1000
            frame_cost_small = system_size_smaller * frame_cost_per_watt * 1000
            frame_cost_large = system_size_larger * frame_cost_per_watt * 1000
            total_cost_recommended = calculate_total_cost(panels_needed, inverter_price_rec, installation_rec, frame_cost_rec)
            total_cost_smaller = calculate_total_cost(math.ceil(system_size_smaller * 1000 / panel_power), inverter_price_small, installation_small, frame_cost_small)
            total_cost_larger = calculate_total_cost(math.ceil(system_size_larger * 1000 / panel_power), inverter_price_large, installation_large, frame_cost_large)

            # Prepare response data for all three systems
            response_data = {
                'name': name,
                'address': address,
                'phone': phone_number,
                'reference_number': reference_number,
                'electricity_bill': invoice_data['Payable Within Due Date'],
                'monthly_units': invoice_data['Units Consumed'],
                'yearly_units': invoice_data['Total Yearly Units'],
                'panel_price': panel_price,
                'panel_brand': panel_brand,
                'panel_power': panel_power,
                'net_metering': net_metering,               
                # Recommended system
                'recommended': {
                    'system_size': system_size_recommended,

                    'panel_quantity': panels_needed,
                    'inverter_brand': inverter_rec.brand,
                    'inverter_price_rec': inverter_price_rec,
                    'frame_cost': frame_cost_rec,
                    'installation_cost': installation_rec,
                    'total_cost': total_cost_recommended,
                    'cabling_cost': 50000,
                    'electrical_and_mechanical_cost': 50000
                },
                # Smaller system
                'smaller': {
                    'system_size': system_size_smaller,
                    'panel_quantity': math.ceil(system_size_smaller * 1000 / panel_power),
                    'inverter_brand': inverter_small.brand,
                    'frame_cost': frame_cost_small,
                    'installation_cost': installation_small,
                    'total_cost': total_cost_smaller,
                    'inverter_price_small': inverter_price_small,
                    'cabling_cost': 50000,
                    'electrical_and_mechanical_cost': 50000
                },
                # Larger system
                'larger': {
                    'system_size': system_size_larger,
                    'panel_quantity': math.ceil(system_size_larger * 1000 / panel_power),
                    'inverter_brand': inverter_large.brand,
                    'frame_cost': frame_cost_large,
                    'installation_cost': installation_large,
                    'total_cost': total_cost_larger,
                    'inverter_price_large': inverter_price_large,
                    'cabling_cost': 50000,
                    'electrical_and_mechanical_cost': 50000
                }
            }
            
            return JsonResponse(response_data)

        except Exception as e:
            return render(request, 'index.html', {'error_message': str(e)})

    return redirect(reverse('your_form_page_name'))

def generate_invoice_for_system(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        system_size = data.get('system_size')
        panel_amount = data.get('panel_amount')
        panel_power = data.get('panel_power')
        inverter_price = data.get('inverter_price')
        inverter_brand = data.get('inverter_brand')
        print(data.get('panel_price'))
        price_of_panels = float(data.get('panel_price')) * int(panel_amount) * float(panel_power)
        net_metering = data.get('net_metering')
        total_cost = data.get('total_cost')
        if total_cost is not None:
            try:
                total_cost = float(total_cost)
            except ValueError:
                total_cost = 0.0  # or any default value you prefer
        else:
            total_cost = 0.0
        customer_name = data.get('customer_name')
        print(customer_name)
        customer_address = data.get('customer_address')
        customer_contact = data.get('customer_contact')
        installation_cost_per_watt = data.get('installation_cost')
        frame_cost_per_watt = data.get('frame_cost')
        cabling_cost = data.get('cabling_cost')
        electrical_and_mechanical_cost = data.get('electrical_and_mechanical_cost')
        #generate_invoice(system_size, panel_amount, panel_power, inverter_price, inverter_brand, price_of_panels, net_metering, installation_cost_per_watt, cabling_cost, frame_cost_per_watt, electrical_and_mechanical_cost, total_cost, customer_name, customer_address, customer_contact)
        invoice_data = {
            'system_size': system_size,
            'panel_amount': panel_amount,
            'panel_power': panel_power,
            'inverter_price': inverter_price,
            'inverter_brand': inverter_brand,
            'price_of_panels': price_of_panels,
            'net_metering': net_metering,
            'total_cost': total_cost,
            'customer_name': customer_name,
            'customer_address': customer_address,
            'customer_contact': customer_contact,
            'installation_cost_per_watt': installation_cost_per_watt,
            'frame_cost_per_watt': frame_cost_per_watt,
            'cabling_cost': cabling_cost,
            'electrical_and_mechanical_cost': electrical_and_mechanical_cost
        }
        # Logic to generate the invoice based on the data
        # Example: Create an invoice record, generate a PDF, etc.

        # Return a success response
        return JsonResponse(invoice_data)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

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
        )
        return JsonResponse({'message': 'Panel added successfully!'})
    
def set_default_panel(request, panel_id):
    # Set all default_choice fields to False
    Panel.objects.update(default_choice=False)

    # Set the selected panel's default_choice to True
    try:
        panel = Panel.objects.get(id=panel_id)
        panel.default_choice = True
        panel.save()
        return JsonResponse({'success': True})
    except Panel.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Panel not found'}, status=404)

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
        variableCosts.objects.update_or_create(
            cost_name='Net Metering', defaults={'cost': data['netMetering']}
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
        net_metering = variableCosts.objects.filter(cost_name='Net Metering').first()
        print(net_metering.cost)
        response_data = {
            'frame_cost_per_watt': frame_cost.cost if frame_cost else '',
            'installation_cost_per_watt': installation_cost.cost if installation_cost else '',
            'net_metering': net_metering.cost if net_metering else ''
        }
        return JsonResponse(response_data, safe=False)
