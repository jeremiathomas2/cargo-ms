from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q

from .models import Customer, CustomerAddress, CustomerContact

ITEMS_PER_PAGE = 25


@login_required
def customer_list(request):
    queryset = Customer.objects.all()

    search = request.GET.get('q', '')
    status = request.GET.get('status', '')
    customer_type = request.GET.get('type', '')

    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(company_name__icontains=search) |
            Q(customer_number__icontains=search) |
            Q(email__icontains=search) |
            Q(phone__icontains=search)
        )
    if status:
        queryset = queryset.filter(status=status)
    if customer_type:
        queryset = queryset.filter(customer_type=customer_type)

    paginator = Paginator(queryset, ITEMS_PER_PAGE)
    page = request.GET.get('page', 1)
    customers = paginator.get_page(page)

    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'search': search,
        'status_filter': status,
        'type_filter': customer_type,
        'status_choices': Customer.STATUS_CHOICES,
        'type_choices': Customer.CUSTOMER_TYPE_CHOICES,
    })


@login_required
def customer_create(request):
    if request.method == 'POST':
        try:
            customer_type = request.POST.get('customer_type', 'individual')
            phone = request.POST.get('phone', '').strip()

            if not phone:
                messages.error(request, 'Phone number is required.')
                return redirect('customers:create')

            from core.utils import generate_document_number
            customer_number = generate_document_number('CUS')

            customer = Customer(
                customer_number=customer_number,
                customer_type=customer_type,
                first_name=request.POST.get('first_name', ''),
                last_name=request.POST.get('last_name', ''),
                company_name=request.POST.get('company_name', ''),
                email=request.POST.get('email', ''),
                phone=phone,
                secondary_phone=request.POST.get('secondary_phone', ''),
                tax_id=request.POST.get('tax_id', ''),
                status='active',
                credit_limit=float(request.POST.get('credit_limit', 0)),
                payment_terms_days=int(request.POST.get('payment_terms_days', 30)),
                notes=request.POST.get('notes', ''),
                created_by=request.user,
            )
            customer.save()

            addr_line1 = request.POST.get('address_line1', '').strip()
            if addr_line1:
                CustomerAddress.objects.create(
                    customer=customer,
                    address_type=request.POST.get('address_type', 'all'),
                    label=request.POST.get('address_label', ''),
                    address_line1=addr_line1,
                    address_line2=request.POST.get('address_line2', ''),
                    city=request.POST.get('city', ''),
                    region=request.POST.get('region', ''),
                    country=request.POST.get('country', 'Tanzania'),
                    postal_code=request.POST.get('postal_code', ''),
                    contact_person=request.POST.get('contact_person', ''),
                    contact_phone=request.POST.get('contact_phone', ''),
                    is_default=True,
                )

            contact_name = request.POST.get('contact_name', '').strip()
            if contact_name:
                CustomerContact.objects.create(
                    customer=customer,
                    name=contact_name,
                    title=request.POST.get('contact_title', ''),
                    email=request.POST.get('contact_email', ''),
                    phone=request.POST.get('contact_phone_number', ''),
                    is_primary=True,
                )

            messages.success(request, f'Customer {customer.full_name} created successfully.')
            return redirect('customers:detail', pk=customer.pk)

        except Exception as e:
            messages.error(request, f'Error creating customer: {str(e)}')

    return render(request, 'customers/customer_form.html', {
        'editing': False,
        'type_choices': Customer.CUSTOMER_TYPE_CHOICES,
    })


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    addresses = customer.addresses.all()
    contacts = customer.contacts.all()
    recent_shipments = customer.shipments.filter(is_deleted=False).order_by('-created_at')[:20]
    invoices = customer.invoices.all()[:10]

    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'addresses': addresses,
        'contacts': contacts,
        'recent_shipments': recent_shipments,
        'invoices': invoices,
    })


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    if request.method == 'POST':
        try:
            customer.customer_type = request.POST.get('customer_type', customer.customer_type)
            customer.first_name = request.POST.get('first_name', customer.first_name)
            customer.last_name = request.POST.get('last_name', customer.last_name)
            customer.company_name = request.POST.get('company_name', customer.company_name)
            customer.email = request.POST.get('email', customer.email)
            customer.phone = request.POST.get('phone', customer.phone)
            customer.secondary_phone = request.POST.get('secondary_phone', customer.secondary_phone)
            customer.tax_id = request.POST.get('tax_id', customer.tax_id)
            customer.status = request.POST.get('status', customer.status)
            customer.credit_limit = float(request.POST.get('credit_limit', customer.credit_limit))
            customer.payment_terms_days = int(request.POST.get('payment_terms_days', customer.payment_terms_days))
            customer.notes = request.POST.get('notes', customer.notes)
            customer.is_watchlisted = request.POST.get('is_watchlisted') == 'on'
            customer.watchlist_reason = request.POST.get('watchlist_reason', customer.watchlist_reason)
            customer.save()

            messages.success(request, f'Customer {customer.full_name} updated successfully.')
            return redirect('customers:detail', pk=customer.pk)

        except Exception as e:
            messages.error(request, f'Error updating customer: {str(e)}')

    return render(request, 'customers/customer_form.html', {
        'customer': customer,
        'editing': True,
        'type_choices': Customer.CUSTOMER_TYPE_CHOICES,
    })
