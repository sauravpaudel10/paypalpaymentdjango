from django.conf import settings
import paypalrestsdk
from django.views.generic import FormView, TemplateView
from django.shortcuts import redirect
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.signals import valid_ipn_received
from paypal.standard.models import ST_PP_COMPLETED
from django.dispatch import receiver
from .models import Transaction
import logging
from .forms import *
from django.shortcuts import render, redirect
from bs4 import BeautifulSoup
from django.contrib import messages
import requests
from django.contrib.auth.decorators import login_required






















class PaypalFormView(FormView):
    template_name = 'process_payment.html'
    form_class = PayPalPaymentsForm

    def get_initial(self):
        paypalrestsdk.configure({
            "mode": "sandbox",  # Change to "live" for production environment
            "client_id": settings.PAYPAL_CLIENT_ID,
            "client_secret": settings.PAYPAL_SECRET
        })
        user = self.request.user
        invoice_number = f'{user.id}'
        plan_id = "P-5ML4271244454362WXNWU5NQ"  # Replace with your PayPal subscription plan ID
        return {
            'business': 'sb-c47axg26184460@business.example.com',
            'amount': 1.99,
            'currency_code': 'USD',
            'item_name': 'Example item',
            'invoice': invoice_number,
            'notify_url': self.request.build_absolute_uri(reverse('paypal-ipn')),
            'return_url': self.request.build_absolute_uri(reverse('paypal-return')),
            'cancel_return': self.request.build_absolute_uri(reverse('paypal-cancel')),
            'lc': 'EN',
            'no_shipping': '1',
            'cmd': '_xclick-subscriptions',
            'a3': '1.99',
            'p3': '1',  # Number of billing cycles (trial period)
            't3': 'M',  # Trial period interval (M for months)
            'src': '1',  # Allow subscribers to modify their subscription
            'sra': '1',  # Reattempt on payment failure
            'no_note': '1',  # Hide note to seller field
            'item_number': plan_id,  # PayPal subscription plan ID
        }


class PaypalReturnView(TemplateView):
    template_name = 'payment_done.html'

    def get(self, request, *args, **kwargs):
        user = request.user

        # Check if the user has any paid transaction
        if user.is_authenticated and user.transactions.filter(paid=True).exists():
            # Redirect the user to the desired page
            return redirect('crawl')
        else:
            # No payment found, redirect to cancel page
            return redirect('paypal-cancel')







class PaypalCancelView(TemplateView):
    template_name = 'payment_cancel.html'


@receiver(valid_ipn_received)
def paypal_payment_received(sender, **kwargs):
    ipn_obj = sender
    if ipn_obj.payment_status == ST_PP_COMPLETED:
        if ipn_obj.receiver_email != 'sb-c47axg26184460@business.example.com':
            # Not a valid payment
            return

        try:
            my_pk = ipn_obj.invoice
            mytransaction = Transaction.objects.get(pk=my_pk)
            assert ipn_obj.mc_gross == str(mytransaction.amount) and ipn_obj.mc_currency == 'USD'
        except Exception:
            logger.exception('Paypal ipn_obj data not valid!')
        else:
            mytransaction.paid = True
            mytransaction.paypal_plan_id = ipn_obj.item_number  # Save PayPal plan ID
            mytransaction.save()
    else:
        logger.debug('Paypal payment status not completed: %s' % ipn_obj.payment_status)



# @receiver(valid_ipn_received)
# def paypal_payment_received(sender, **kwargs):
#     ipn_obj = sender
#     if ipn_obj.payment_status == ST_PP_COMPLETED:
#         if ipn_obj.receiver_email != 'sb-c47axg26184460@business.example.com':
#             # Not a valid payment
#             return

#         try:
#             my_pk = ipn_obj.invoice
#             mytransaction = Transaction.objects.get(pk=my_pk)
#             assert ipn_obj.mc_gross == str(mytransaction.amount) and ipn_obj.mc_currency == 'EUR'
#         except Exception:
#             logger.exception('Paypal ipn_obj data not valid!')
#         else:
#             mytransaction.paid = True
#             mytransaction.save()
#     else:
#         logger.debug('Paypal payment status not completed: %s' % ipn_obj.payment_status)



logger = logging.getLogger(__name__)














def home(request):
    return render (request , 'home.html')


def subscription(request):
    return render(request , 'subscription.html')



def profile(request):
    return render (request, 'profile.html')
















def premium_user_required(view_func):
    def wrapper(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.paid:
            return view_func(request, *args, **kwargs)
        else:
            # Redirect or display an error message for non-premium users
            return render(request, 'subscription.html')
    return wrapper



@premium_user_required
@login_required
def crawl_website_properly(request):

    if request.method == 'POST':
        url = request.POST.get('url')  
       
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        page_title = soup.title.text if soup.title else None

        urls = [link['href'] for link in soup.find_all('a', href=True)]

        meta_tags = soup.find_all('meta')
        metadata = {}
        for tag in meta_tags:
            if tag.get('name'):
                metadata[tag.get('name')] = tag.get('content')

        headings = [heading.text for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

        text_content = soup.get_text()

        images = []
        img_tags = soup.find_all('img')
        for img in img_tags:
            img_src = img.get('src')
            alt_text = img.get('alt')
            images.append({'src': img_src, 'alt': alt_text})

        structured_data = soup.find_all('script', type='application/ld+json')

        return render(request, 'crawl_result.html', {
            'page_title': page_title,
            'urls': urls,
            'metadata': metadata,
            'headings': headings,
            'text_content': text_content,
            'images': images,
            'structured_data': structured_data
        })

    return render(request, 'crawl_result.html')




































def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'account created for {username}! ')
            return redirect ('home')
    else:
       form = UserRegisterForm()
    content = {'form' : form}
    return render (request, 'register.html',content)


