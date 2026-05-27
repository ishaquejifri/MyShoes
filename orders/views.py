from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse
import string,random
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from cart.models import Cart
from .models import Order,OrderItem
from accounts.models import Address
from category.models import Category
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from io import BytesIO

# Create your views here.

def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))

@login_required
def checkout(request):
    categories = Category.objects.filter(is_active=True)
    cart = get_object_or_404(Cart,user=request.user)

    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request,'Your cart is empty')
        return redirect('cart:view_cart')
    
    addresses = Address.objects.filter(user=request.user)

    subtotal = sum(item.subtotal() for item in cart_items)
    shipping_charge = Decimal('0.00')
    total = subtotal + shipping_charge

    context = {
        'categories': categories,
        'cart_items': cart_items,
        'addresses': addresses,
        'subtotal': subtotal,
        'shipping_charge': shipping_charge,
        'total': total,

    }

    return render(request, 'checkout.html', context)

@login_required
def place_order(request):
    if request.method != 'POST':
        return redirect('checkout')
    
    cart = get_object_or_404(Cart,user=request.user)
    cart_items = cart.items.all()

    if not cart_items.exists():
        messages.error(request,'Cart is empty')
        return redirect('cart:view_cart')
    
    address_id = request.POST.get('address_id')

    if not address_id:
        messages.error(request,'Please select an address')
        return request('checkout')
    
    address = get_object_or_404(Address,id=address_id, user=request.user)

    subtotal = sum(item.subtotal() for item in cart_items)

    shipping = 40
    discount = 0
    grand_total = subtotal + shipping - discount

    order = Order.objects.create(
        order_id = generate_order_id(),
        user = request.user,
        shipping_address = address,
        full_name = address.full_name,
        mobile = address.phone,
        street_address = address.address_line,
        city = address.city,
        state = address.state,
        postal_code = address.postal_code,
        payment_method = 'cod',
        sub_total = subtotal,
        shipping_charge = shipping,
        discount_amount = discount,
        total_amount = grand_total,
    )

    for item in cart_items:
        variant = item.variant
        if variant.stock < item.quantity:
            messages.error(request,f"Only{variant.stock} stock available for {item.product.product_name}")
            order.delete()
            return redirect('checkout')
        
        OrderItem.objects.create(
            order = order,
            product = item.product,
            variant = variant,

            product_name = item.product.product_name,
            variant_size = variant.size,
            variant_color = variant.color,

            price = item.price,
            original_price = item.product.base_price,
            discount_amount = item.product.base_price - item.price,
            quantity = item.quantity,
        )

        variant.stock -= item.quantity
        variant.save()

    cart_items.delete()

    messages.success(request,"Order Placed Successfully")

    return redirect('order_success', order_id = order.order_id)

@login_required
def order_success(request,order_id):
    order = get_object_or_404(Order, order_id = order_id, user= request.user)
    categories = Category.objects.filter(is_active=True)
    order_items = order.items.all()


    return render(request,'order_success.html',{
        'order': order,
        'order_items': order_items,
        'categories': categories,
        })

@login_required
def my_order(request):

    

    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    categories = Category.objects.filter(is_active=True)

    context = {
        'orders': orders,
        'categories': categories,
    }

    return render(request,'order_list.html', context)

@login_required
def cancel_order(request,order_id):

    categories = Category.objects.filter(is_active=True)
    order = get_object_or_404(Order, order_id=order_id,user=request.user)

    if order.status == 'Delivered':
        messages.error(request,'Delivered orders cannot be cancelled' )
        return redirect('my_orders')

    if order.status == 'Cancelled':
        messages.warning(request,'Order already cancelled')
        return redirect('my_orders')
    
    if request.method == 'POST':
        reason = request.POST.get('reason')
       
    #Restore stock
        for item in order.items.all():
            if item.item_status == 'Cancelled':
                variant = item.variant

                variant.stock += item.quantity
                variant.save()

                item.item_status = 'Cancelled'
                item.save()

        order.status = 'Cancelled'
        order.cancellation_reason = reason
        order.save()

        messages.success(request, 'Order cancelled Successfully')

        return redirect('order_details', order_id=order.order_id)

    return render(request,'order_cancel.html', { 'order': order }) 


@login_required
def cancel_order_item(request,item_id):

    order_item = get_object_or_404(OrderItem,id=item_id,order__user=request.user)

    if order_item.item_status == 'Delivered':
        messages.error(request, 'Deilivered item cannot be cancelled')
        return redirect('my_orders')

    if order_item.item_status == 'Cancelled':
        messages.warning(request,'Item already cancelled')
        return redirect('my_orders')
    
    #restore stock
    variant = order_item.variant

    variant.stock += order_item.quantity
    variant.save()

    #cancel item
    order_item.item_status = 'Cancelled'
    order_item.save()

    #check all item cancelled
    order = order_item.order

    active_items = order.items.exclude(item_status='Cancelled')

    if not active_items.exists():
        order.item_status = 'Cancelled'
        order.save()

    messages.success(request,'Product cancelled Successfully')

    return redirect('my_orders')

def order_details(request, order_id):

    order = get_object_or_404(Order, order_id = order_id, user = request.user)

    context = {
        'order': order,
        'order_items': order.items.all(),
        'categories': Category.objects.filter(is_active=True),
    }

    return render(request, 'order_details.html', context)

@login_required
def return_order(request, order_id):

    order = get_object_or_404(Order, order_id = order_id, user = request.user) 

    if order.status != 'Delivered':
        messages.error(request, 'Only Delivered Items can be returned')
        return redirect('order_details', order_id = order.order_id)  

    if request.method == 'POST':
        reason = request.POST.get('reason')
        
        # Mandatory reason
        if not reason:
            messages.error(request,'Return reason is required')
            return redirect('return_order_item', order_id = order.order_id) 
        
        # Restore stock
        for item in order.items.all():
            variant = item.variant

            variant.stock += item.quantity
            variant.save()

            item.item_status == 'Returned'
            item.save()

        order.status == 'Returned'
        order.return_reason = reason
        order.save()

        messages.success(request, 'Return request submitted successfully')
        return redirect('my_orders')

    return render(request, 'return_order_item.html', { 'order': order }) 


@login_required
def download_invoice(request, order_id):

    order = get_object_or_404(Order, order_id=order_id, user=request.user)

    # Allow only delivered orders
    if order.status.lower() != "delivered":
        messages.error(request, "Invoice available only after delivery.")
        return redirect("order_details", order_id=order.order_id)

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=28,
    )

    elements = []
    styles = getSampleStyleSheet()

    # TITLE
    title = Paragraph(
        f"<b>Invoice - Order #{order.order_id}</b>",
        styles['Title']
    )
    elements.append(title)
    elements.append(Spacer(1, 20))

    # CUSTOMER INFO (FIXED)
    customer_info = Paragraph(f"""
        <b>Customer Name:</b> {order.full_name}<br/>
        <b>Mobile:</b> {order.mobile}<br/>
        <b>Address:</b> {order.street_address}, {order.city}, {order.state}, {order.postal_code}<br/>
        <b>Payment Method:</b> {order.payment_method}<br/>
        <b>Order Status:</b> {order.status}<br/>
    """, styles['BodyText'])

    elements.append(customer_info)
    elements.append(Spacer(1, 20))

    # TABLE HEADER
    data = [
        ['Product', 'Variant', 'Qty', 'Price', 'Total']
    ]

    # ORDER ITEMS
    for item in order.items.all():

        price = item.product.offer_price   # FIXED
        total_price = item.quantity * price

        data.append([
            item.product_name,
            f"{item.variant_size} / {item.variant_color}",
            str(item.quantity),
            f"₹{price}",
            f"₹{total_price}",
        ])

    # GRAND TOTAL
    data.append([
        '',
        '',
        '',
        'Grand Total',
        f"₹{order.total_amount}"
    ])

    table = Table(data, colWidths=[170, 120, 60, 80, 80])

    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 30))

    footer = Paragraph(
        "Thank you for shopping with Lotto Shoes!",
        styles['BodyText']
    )
    elements.append(footer)

    doc.build(elements)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.order_id}.pdf"'

    response.write(pdf)
    return response


