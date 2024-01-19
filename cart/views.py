from django.shortcuts import render, get_object_or_404, redirect
from .cart import Cart
from store.models import Product
from django.http import JsonResponse
from django.contrib import messages
from django.http import JsonResponse
import stripe
from django.http import HttpResponse



def cart_summary(request):
	# Get the cart
	cart = Cart(request)
	cart_products = cart.get_prods
	quantities = cart.get_quants
	totals = cart.cart_total()

	return render(request, "cart_summary.html", {"cart_products":cart_products, "quantities":quantities, "totals":totals})



def cart_add(request):
	# Get the cart
	cart = Cart(request)
	# test for POST
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		# lookup product in DB
		product = get_object_or_404(Product, id=product_id)
		
		# Save to session
		cart.add(product=product, quantity=product_qty)

		# Get Cart Quantity
		cart_quantity = cart.__len__()

		# Return resonse
		# response = JsonResponse({'Product Name: ': product.name})
		response = JsonResponse({'qty': cart_quantity})
		messages.success(request, ("Product Added To Cart..."))
		return response

def cart_delete(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		# Call delete Function in Cart
		cart.delete(product=product_id)

		response = JsonResponse({'product':product_id})
		#return redirect('cart_summary')
		messages.success(request, ("Item Deleted From Shopping Cart..."))
		return response


def cart_update(request):
	cart = Cart(request)
	if request.POST.get('action') == 'post':
		# Get stuff
		product_id = int(request.POST.get('product_id'))
		product_qty = int(request.POST.get('product_qty'))

		cart.update(product=product_id, quantity=product_qty)

		response = JsonResponse({'qty':product_qty})
		#return redirect('cart_summary')
		messages.success(request, ("Your Cart Has Been Updated..."))
		return response


# Set your Stripe API key
stripe.api_key = "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" 


def create_payment_link(request):
    amount =  5000 # Amount in cents (e.g., $50.00)
    currency = "usd"
    success_url = "http://localhost:8000/success/"  # Update with your success URL
    cancel_url = "http://localhost:8000/cancel/"  # Update with your cancel URL

    try:
        line_items = [{
            'price_data': {
                'currency': currency,
                'unit_amount': amount,
                'product_data': {
                    'name': 'Payment'
                },
            },
            'quantity': 1,
        }]
        payment_link = stripe.checkout.Session.create(
            success_url=success_url,
            cancel_url=cancel_url,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
        )

        # Retrieve the payment link URL
        link_url = payment_link.url
		

        # Render the template with the payment link
        return render(request, 'cart_summary.html', {'link_url': link_url})

    except stripe.error.StripeError as e:
        # Handle any errors that occur during payment link creation
        print (f"Error creating payment link: {e}")
        return render('payment_error.html')