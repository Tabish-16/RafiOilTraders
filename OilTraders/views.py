from django.shortcuts import redirect, render,HttpResponse
from django.contrib.auth import authenticate, login as auth_login,logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from OilTraders.models import *
from sms import send_sms
from django.core import serializers 
from fpdf import FPDF
import pywhatkit as kit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os

os.environ['DISPLAY'] = ':0

def whatsappsender(phone_number, name, registeration_num, last_reading, next_reading, next_changing_date):
    try:
        # Construct the message with newline characters
        message = (
            f"Thank you Mr. {name} for choosing us.\n\n"
            f"Last reading: {last_reading}\n"
            f"Next oil change reading: {next_reading}\n"
            f"Next change date: {next_changing_date}"
        )
        
        # Send the WhatsApp message instantly
        kit.sendwhatmsg_instantly(phone_number, message)
        return "Message Sent Instantly!"
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")
        return f"Failed to send message: {e}"


def send_whatsapp_reminder(phone_number, name, next_changing_date):
    try:
        # Message template
        message = (
            f"Reminder: Dear {name}, it's time to check your vehicle.\n"
            f"Your next oil change is scheduled for {next_changing_date}.\n"
            f"Please visit us soon!"
        )
        # Send WhatsApp message instantly
        kit.sendwhatmsg_instantly(phone_number, message)
        print(f"Reminder sent to {name}")
    except Exception as e:
        print(f"Failed to send WhatsApp message: {e}")

# Function to check which customers need reminders and send them
def check_and_send_reminders():
    # Get current date
    current_date = datetime.now().date()
    
    # Fetch all customers from the database
    customers = NewEntry.objects.all()
    
    for customer in customers:
        # Check if 15 days have passed since the last oil change date
        last_oil_change_date = customer.date  # The date the customer last changed oil
        next_reminder_date = last_oil_change_date + timedelta(days=15)  # Reminder 15 days later
        
        if current_date >= next_reminder_date:
            # Send reminder via WhatsApp
            send_whatsapp_reminder(customer.phone_number, customer.name, customer.next_changing_date)
            
            # Update the last oil change date (reset for the next 15 days cycle)
            customer.date = current_date  # Reset the date to the current date for the next cycle
            customer.save()  # Save the updated date to the database

# Function to start the scheduler
def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Schedule the check_and_send_reminders function to run once every day
    scheduler.add_job(check_and_send_reminders, 'interval', days=1)
    
    # Start the scheduler in the background
    scheduler.start()

# Call this function when your Django app starts (e.g., in apps.py or settings.py)
start_scheduler()


def home(request):
    context = {}
    if request.method == 'POST':
        search = request.POST.get('search_input', '').lower()
        if search and 'search' in request.POST:
            filter_entries = NewEntry.objects.filter(registeration_num=search)
            context['filter'] = filter_entries if filter_entries.exists() else None
            if not filter_entries.exists():
                context['message'] = "No entries found matching the search criteria."
    return render(request, 'index.html', context)


def login(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        
        user = authenticate(request, username=name, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('dashboard')  # Redirect to a home page or any other page
        else:
            return redirect('home')


def logoutUser(request):
    if request.user.is_authenticated:
        print(request.user)
        auth_logout(request)
    else:    
        return redirect("home")
    return redirect('home')    
@login_required        
def dashboard(request):
    entries = NewEntry.objects.all().order_by('-id')
    oil_companies = Oil_Companies.objects.all()
    
    all_oil = serializers.serialize('json',oil_companies)    
    existing_entries = serializers.serialize('json', entries)    
    
    return render(request,'dashboard.html',{'entries':entries,'existing_entries':existing_entries,"all_oil":all_oil})




def new_entry(request):
    try:
        if request.method == 'POST':
            customer_id = request.POST.get('customer_id')
            name = request.POST.get('name')
            phone_number = request.POST.get('phone') 
            vehicle = request.POST.get('vehicle') 
            registeration_num = request.POST.get('registration_num').lower() 
            date = request.POST.get('date') 
            last_reading = request.POST.get('last_reading') 
            next_reading = request.POST.get('next_reading') 
            next_changing_date = request.POST.get('next_changing_date')
            oil_company_id = request.POST.get('oil_company')
            oil_quantity = request.POST.get('oil_quantity')
            oil_filter = request.POST.get('oil_filter')
            ac_filter = request.POST.get('ac_filter')
            air_filter = request.POST.get('air_filter')
            oil_price = request.POST.get('oil_price')
            
            
            oil_company = Oil_Companies.objects.get(id=oil_company_id)
            if customer_id:
                # Update existing customer
                customer = NewEntry.objects.get(id=customer_id)
                customer.name = name
                customer.phone_number = phone_number
                customer.vehicle = vehicle
                customer.registeration_num = registeration_num
                customer.date = date
                customer.last_reading = last_reading
                customer.next_reading = next_reading
                customer.next_changing_date = next_changing_date
                customer.oil_companies = oil_company
                customer.oil_quantity = oil_quantity
                customer.oil_filter = oil_filter
                customer.ac_filter = ac_filter
                customer.air_filter = air_filter
                customer.oil_price = oil_price
                customer.save()
                whatsappsender(phone_number,name,registeration_num,last_reading,next_reading,next_changing_date)
            else:
                # Create new customer
                NewEntry.objects.create(
                    name=name,
                    phone_number=phone_number,
                    vehicle=vehicle,
                    registeration_num=registeration_num,
                    date=date,
                    last_reading=last_reading,
                    next_reading=next_reading,
                    next_changing_date=next_changing_date,
                    oil_companies = oil_company,
                    oil_quantity = oil_quantity,
                    oil_filter = oil_filter,
                    ac_filter = ac_filter,
                    air_filter = air_filter,
                    oil_price = oil_price,
                )
                whatsappsender(phone_number,name,registeration_num,last_reading,next_reading,next_changing_date)
            
            return redirect('dashboard')
    except Exception as e:
        print("error",e)
        return HttpResponse("Bad Request",e)    
    
    
    #send sms 




class POSReceipt(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', (80, 150))

    def header(self):
        pass

    def footer(self):
        pass

def invoice_pdf(request,pk):
    # Create instance of POSReceipt
    pdf = POSReceipt()

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial","B" ,size=14)

    
    
    invoice = NewEntry.objects.get(id=pk)
    # Add content
    pdf.set_fill_color(28, 28, 28) 
    pdf.rect(0,0,80,20,"DF")
    pdf.image("static/assets/logo.png", x=10, y=6, w=10, h=10)
    pdf.set_text_color(122, 122, 122)
    pdf.text(46,12,"Oil Traders")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B",size=10)
    pdf.set_y(25)
    pdf.cell(35, 10, f"Name",)
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, invoice.name, ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Phone Number", )
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, invoice.phone_number, ln=True,)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Vehicle", )
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, invoice.vehicle, ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Registration num")
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, invoice.registeration_num, ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Date")
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, str(invoice.date), ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Last Reading")
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, invoice.last_reading, ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Next Reading")
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, invoice.next_reading, ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Changing Date")
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, str(invoice.next_changing_date), ln=True)
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(0, 10, "---------------------------", ln=True,align="C")
    
    pdf.set_y(40)
    pdf.set_fill_color(28, 28, 28) 
    pdf.rect(0,130,80,20,"DF")
    pdf.set_text_color(122, 122, 122)
    pdf.set_font("Arial", "B",size=9)
    pdf.text(3,135,"Contact Us")
    pdf.text(3,139,"03185858855")
    pdf.text(3,143,"03185858855")
    pdf.text(50,135,"Our Location")
    pdf.text(45,139,"Wah Cantt GT Road ")

    # Get the PDF content as a string
    pdf_output = pdf.output(dest='S').encode('latin1')

    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(pdf_output, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response




class POSBill(FPDF):
    def __init__(self):
        super().__init__('P', 'mm', (80, 150))

    def header(self):
        pass

    def footer(self):
        pass

def bill_pdf(request,pk):
    # Create instance of POSReceipt
    pdf = POSBill()

    # Add a page
    pdf.add_page()

    # Set font
    pdf.set_font("Arial","B" ,size=14)

    
    
    bill = NewEntry.objects.get(id=pk)
    # Add content
    pdf.set_fill_color(28, 28, 28) 
    pdf.rect(0,0,80,20,"DF")
    pdf.image("static/assets/logo.png", x=10, y=6, w=10, h=10)
    pdf.set_text_color(122, 122, 122)
    pdf.text(46,12,"Oil Traders")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B",size=10)
    pdf.set_y(25)
    
    
    
    
    
    
    pdf.cell(35, 10, f"Oil Brand & Grade",)
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, str(bill.oil_companies), ln=True)
    
    if bill.oil_quantity:
        pdf.set_font("Arial", "B",size=10)
        pdf.cell(35, 10, f"Oil Quantity", )
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, bill.oil_quantity +"/Litre", ln=True,)
    
    if bill.oil_price:
        pdf.set_font("Arial", "B",size=10)
        pdf.cell(35, 10, f"Oil Amount", )
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, bill.oil_price +"/-", ln=True)
    
    if bill.oil_filter:
        pdf.set_font("Arial", "B",size=10)
        pdf.cell(35, 10, f"Oil Filter")
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, bill.oil_filter +"/-", ln=True)
    
    if bill.ac_filter:
        pdf.set_font("Arial", "B",size=10)
        pdf.cell(35, 10, f"A/C Filter")
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, bill.ac_filter +"/-", ln=True)
    
    if bill.air_filter:
        pdf.set_font("Arial", "B",size=10)
        pdf.cell(35, 10, f"Air Filter")
        pdf.set_font("Arial", size=10)
        pdf.cell(40, 10, bill.air_filter +"/-", ln=True)
    
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(0, 10, "----------------------------------------------------", ln=True,align="C")
    
    pdf.set_font("Arial", "B",size=10)
    pdf.cell(35, 10, f"Total")
    
    total = int(bill.oil_price or 0) + int(bill.oil_filter or 0) + int(bill.ac_filter or 0) + int(bill.air_filter or 0)
    
    pdf.set_font("Arial", size=10)
    pdf.cell(40, 10, str(total) +"/-", ln=True)
    pdf.set_font("Arial", "B",size=10)
    
    
    pdf.set_y(40)
    pdf.set_fill_color(28, 28, 28) 
    pdf.rect(0,130,80,20,"DF")
    pdf.set_text_color(122, 122, 122)
    pdf.set_font("Arial", "B",size=9)
    pdf.text(3,135,"Contact Us")
    pdf.text(3,139,"03185858855")
    pdf.text(3,143,"03185858855")
    pdf.text(50,135,"Our Location")
    pdf.text(45,139,"Wah Cantt GT Road ")

    # Get the PDF content as a string
    pdf_output = pdf.output(dest='S').encode('latin1')

    # Create the HttpResponse object with the appropriate PDF headers
    response = HttpResponse(pdf_output, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="invoice.pdf"'

    return response
