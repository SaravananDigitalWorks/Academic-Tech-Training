from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
from datetime import *
from .forms import *
from django.contrib.auth import *
from django.http import *
from .utils import *

def index(request) :
    return render(request,'inventory/index.html')
def auth_logout(request):
    logout(request)
    return redirect('inventory:home')
@login_required
def add_product(request):
    if not request.user.is_superuser and not request.user.is_supervisor:
        messages.error(request, "You do not have permission to add products.")
        return redirect('home')

    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('inventory:product_list')  # Redirect to the product list page
    else:
        form = ProductForm()
    
    return render(request, 'inventory/add_product.html', {'form': form})


@login_required
def expiring_products(request):
    if not request.user.is_salesperson():
        return redirect('home')

    expiring_products = Product.objects.filter(expiry_date__lte=datetime.now().date() + timedelta(days=3))
    
    return render(request, "inventory/expiring_products.html", {"products": expiring_products})
def product_list(request):
    products = Product.objects.all()  # Fetch all products
    return render(request, 'inventory/product_list.html', {'products': products})

     
def about(request):
    return render(request, 'inventory/about.html')

def contact(request):
     return render(request, 'inventory/contact.html')

def send_message_view(request):
    message = "Hello from Django Telegram Bot!"
    response = send_telegram_message(message)
    return HttpResponse("Message Sent")

def send_expiring_products_to_telegram(request) :
    if request.method == "POST" :
        if request.user.is_superuser:
            products = Product.objects.filter(expiry_date__lte=datetime.now().date() + timedelta(days=3))
            if products :
                message = "📢 *Expiring Product List:*\n\n"
                for product in products:
                    message += f"*{product.name}*\n Category : {product.grocery_type}\n MFD: {product.manufacturing_date}\n EXP: {product.expiry_date}\n\n"
                response = send_telegram_message(message)
                if response.get("ok"):
                    return JsonResponse({"status": "success", "message": "Message sent!"})
                else:
                    return JsonResponse({"status": "error", "message": "Failed to send message."})

                return JsonResponse({"status": "error", "message": "Invalid request method."})
            else :
               return JsonResponse({"status": "success", "message": "No expiring products!"}) 








