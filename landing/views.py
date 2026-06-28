from django.shortcuts import render

# Create your views here.
from django.shortcuts import render


def home(request):
    return render(request, 'landing/home.html')


def about(request):
    return render(request, 'landing/about.html')


def contact(request):
    from django.contrib import messages
    if request.method == 'POST':
        name    = request.POST.get('name', '')
        email   = request.POST.get('email', '')
        message = request.POST.get('message', '')
        # You can add email sending here later
        messages.success(request, f"Thanks {name}! We'll get back to you at {email} shortly.")
    return render(request, 'landing/contact.html')