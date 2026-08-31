"""
Management command to seed initial data for the Cargo Management System.
This includes roles, permissions, users, organizations, branches, and customers.
"""
import uuid
from decimal import Decimal
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from accounts.models import Role, Permission
from saas_config.models import Organization
from branches.models import Branch, BranchSetting
from customers.models import Customer, CustomerAddress, CustomerContact
from cargo.models import Shipment


User = get_user_model()


class Command(BaseCommand):
    help = "Seed initial data for the Cargo Management System"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write(self.style.WARNING('Clearing existing data...'))
            self.clear_data()

        self.stdout.write(self.style.SUCCESS('Starting data seeding...'))

        try:
            # Seed roles and permissions
            self.seed_roles_and_permissions()
            
            # Seed organizations
            org = self.seed_organizations()
            
            # Seed super admin user
            self.seed_admin_user()
            
            # Seed branches
            branches = self.seed_branches(org)
            
            # Seed customers
            customers = self.seed_customers(org)
            
            # Seed regular users
            self.seed_users(org, branches)
            
            # Seed shipments for chart data
            self.seed_shipments(org, customers, branches)
            
            self.stdout.write(
                self.style.SUCCESS('✓ Data seeding completed successfully!')
            )
        except Exception as e:
            raise CommandError(f'Error during data seeding: {str(e)}')

    def clear_data(self):
        """Clear existing data (use with caution)"""
        try:
            User.objects.filter(is_superuser=False).delete()
            Customer.objects.all().delete()
            Branch.objects.filter(is_headquarters=False).delete()
            Organization.objects.filter(name__ne='Default Organization').delete()
            Role.objects.all().delete()
            Permission.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Warning during data clearing: {e}'))

    def seed_roles_and_permissions(self):
        """Create roles and permissions"""
        self.stdout.write('Creating roles and permissions...')
        
        # Define roles
        roles_data = [
            ('super_admin', 'Super Administrator', 'Full system access'),
            ('system_admin', 'System Administrator', 'System administration'),
            ('head_office_manager', 'Head Office Manager', 'Head office management'),
            ('branch_manager', 'Branch Manager', 'Branch operations management'),
            ('booking_officer', 'Booking Officer', 'Cargo booking and booking management'),
            ('customer_service', 'Customer Service Officer', 'Customer service and support'),
            ('warehouse_officer', 'Warehouse Officer', 'Warehouse operations'),
            ('dispatch_officer', 'Dispatch Officer', 'Cargo dispatch and loading'),
            ('transport_manager', 'Transport Manager', 'Transportation management'),
            ('driver', 'Driver', 'Vehicle and cargo handling'),
            ('delivery_officer', 'Delivery Officer', 'Last-mile delivery'),
            ('accountant', 'Accountant', 'Financial records'),
            ('finance_manager', 'Finance Manager', 'Financial management'),
            ('auditor', 'Auditor', 'System auditing'),
            ('customer', 'Customer', 'Customer portal access'),
        ]
        
        for role_name, display_name, description in roles_data:
            role, created = Role.objects.get_or_create(
                name=role_name,
                defaults={
                    'display_name': display_name,
                    'description': description,
                    'is_active': True,
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created role: {display_name}')
            else:
                self.stdout.write(f'  → Role exists: {display_name}')
        
        # Define permissions (module and action pairs)
        permissions_data = [
            ('cargo', 'view'), ('cargo', 'create'), ('cargo', 'update'), ('cargo', 'delete'),
            ('package', 'view'), ('package', 'create'), ('package', 'update'), ('package', 'delete'),
            ('warehouse', 'view'), ('warehouse', 'manage'), ('warehouse', 'receive'), ('warehouse', 'dispatch'),
            ('vehicle', 'view'), ('vehicle', 'manage'), ('vehicle', 'assign'),
            ('driver', 'view'), ('driver', 'manage'), ('driver', 'assign'),
            ('gps', 'view'), ('gps', 'manage'),
            ('payment', 'view'), ('payment', 'manage'), ('payment', 'refund'),
            ('invoice', 'view'), ('invoice', 'create'), ('invoice', 'export'),
            ('document', 'view'), ('document', 'manage'),
            ('report', 'view'), ('report', 'export'),
            ('user', 'view'), ('user', 'create'), ('user', 'update'), ('user', 'delete'),
            ('settings', 'view'), ('settings', 'manage'),
            ('audit', 'view'), ('audit', 'export'),
        ]
        
        for module, action in permissions_data:
            perm, created = Permission.objects.get_or_create(
                module=module,
                action=action,
                defaults={
                    'description': f'Can {action} {module} records',
                }
            )
            if created:
                self.stdout.write(f'  ✓ Created permission: {module}.{action}')

    def seed_organizations(self):
        """Create test organization"""
        self.stdout.write('Creating organizations...')
        
        org, created = Organization.objects.get_or_create(
            slug='cargo-management-solutions',
            defaults={
                'name': 'Cargo Management Solutions',
                'timezone': 'Africa/Dar_es_Salaam',
                'currency': 'TZS',
                'is_active': True,
                'plan': 'enterprise',
                'max_users': 500,
                'max_shipments': 10000,
            }
        )
        
        if created:
            self.stdout.write(f'  ✓ Created organization: {org.name}')
        else:
            self.stdout.write(f'  → Organization exists: {org.name}')
        
        return org

    def seed_admin_user(self):
        """Create superuser for admin access"""
        self.stdout.write('Creating admin user...')
        
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@cargo-ms.com',
                password='admin123',
                first_name='System',
                last_name='Administrator',
            )
            admin.is_staff = True
            admin.is_active = True
            admin.save()
            self.stdout.write('  ✓ Created superuser: admin')
            self.stdout.write('  → Username: admin')
            self.stdout.write('  → Password: admin123')
            self.stdout.write('  → Email: admin@cargo-ms.com')
        else:
            self.stdout.write('  → Superuser already exists: admin')

    def seed_branches(self, organization):
        """Create test branches"""
        self.stdout.write('Creating branches...')
        
        branches_data = [
            {
                'name': 'Dar es Salaam Head Office',
                'code': 'HQ-DES',
                'address': '123 Main Street, Dar es Salaam',
                'city': 'Dar es Salaam',
                'phone': '+255 22 123 4567',
                'email': 'hq@cargo-ms.com',
                'latitude': Decimal('-6.7924'),
                'longitude': Decimal('39.2083'),
                'is_headquarters': True,
            },
            {
                'name': 'Arusha Branch',
                'code': 'BR-ARU',
                'address': '456 Airport Road, Arusha',
                'city': 'Arusha',
                'phone': '+255 27 254 7890',
                'email': 'arusha@cargo-ms.com',
                'latitude': Decimal('-3.3869'),
                'longitude': Decimal('36.6830'),
                'is_headquarters': False,
            },
            {
                'name': 'Mbeya Branch',
                'code': 'BR-MBE',
                'address': '789 Southern Road, Mbeya',
                'city': 'Mbeya',
                'phone': '+255 25 250 1234',
                'email': 'mbeya@cargo-ms.com',
                'latitude': Decimal('-8.9050'),
                'longitude': Decimal('33.4462'),
                'is_headquarters': False,
            },
        ]
        
        branches = []
        for branch_data in branches_data:
            branch, created = Branch.objects.get_or_create(
                code=branch_data['code'],
                defaults={
                    'organization': organization,
                    'name': branch_data['name'],
                    'address': branch_data['address'],
                    'city': branch_data['city'],
                    'phone': branch_data['phone'],
                    'email': branch_data['email'],
                    'latitude': branch_data['latitude'],
                    'longitude': branch_data['longitude'],
                    'is_headquarters': branch_data['is_headquarters'],
                    'is_active': True,
                }
            )
            
            if created:
                # Create branch settings
                BranchSetting.objects.get_or_create(
                    branch=branch,
                    defaults={
                        'timezone': 'Africa/Dar_es_Salaam',
                        'currency': 'TZS',
                        'auto_receive': False,
                        'auto_dispatch': False,
                        'gps_required': True,
                        'insurance_default': False,
                    }
                )
                self.stdout.write(f'  ✓ Created branch: {branch.name}')
                branches.append(branch)
            else:
                self.stdout.write(f'  → Branch exists: {branch.name}')
                branches.append(branch)
        
        return branches

    def seed_customers(self, organization):
        """Create test customers"""
        self.stdout.write('Creating customers...')
        
        customers_data = [
            {
                'customer_type': 'company',
                'first_name': '',
                'last_name': '',
                'company_name': 'ABC Trading Ltd',
                'email': 'info@abc-trading.com',
                'phone': '+255 22 111 1111',
                'tax_id': 'TZN-123-456-789',
                'credit_limit': Decimal('50000.00'),
                'payment_terms_days': 30,
            },
            {
                'customer_type': 'company',
                'first_name': '',
                'last_name': '',
                'company_name': 'XYZ Logistics',
                'email': 'info@xyz-logistics.com',
                'phone': '+255 22 222 2222',
                'tax_id': 'TZN-987-654-321',
                'credit_limit': Decimal('75000.00'),
                'payment_terms_days': 45,
            },
            {
                'customer_type': 'individual',
                'first_name': 'John',
                'last_name': 'Doe',
                'company_name': '',
                'email': 'john.doe@email.com',
                'phone': '+255 65 123 4567',
                'tax_id': '',
                'credit_limit': Decimal('10000.00'),
                'payment_terms_days': 7,
            },
            {
                'customer_type': 'individual',
                'first_name': 'Jane',
                'last_name': 'Smith',
                'company_name': '',
                'email': 'jane.smith@email.com',
                'phone': '+255 65 987 6543',
                'tax_id': '',
                'credit_limit': Decimal('15000.00'),
                'payment_terms_days': 7,
            },
        ]
        
        customers = []
        for idx, customer_data in enumerate(customers_data, 1):
            customer_number = f'CUST{1001 + idx:04d}'
            customer, created = Customer.objects.get_or_create(
                customer_number=customer_number,
                defaults={
                    'organization': organization,
                    'customer_type': customer_data['customer_type'],
                    'first_name': customer_data['first_name'],
                    'last_name': customer_data['last_name'],
                    'company_name': customer_data['company_name'],
                    'email': customer_data['email'],
                    'phone': customer_data['phone'],
                    'tax_id': customer_data['tax_id'],
                    'status': 'active',
                    'credit_limit': customer_data['credit_limit'],
                    'payment_terms_days': customer_data['payment_terms_days'],
                }
            )
            
            if created:
                # Create default address
                CustomerAddress.objects.create(
                    customer=customer,
                    address_type='all',
                    label='Default',
                    address_line1='123 Street Name',
                    city='Dar es Salaam',
                    country='Tanzania',
                    is_default=True,
                )
                
                # Create contact
                CustomerContact.objects.create(
                    customer=customer,
                    name=customer.full_name,
                    phone=customer.phone,
                    email=customer.email,
                    is_primary=True,
                )
                
                self.stdout.write(f'  ✓ Created customer: {customer.full_name}')
            else:
                self.stdout.write(f'  → Customer exists: {customer.full_name}')
            
            customers.append(customer)
        
        return customers

    def seed_users(self, organization, branches):
        """Create test users with different roles"""
        self.stdout.write('Creating test users...')
        
        users_data = [
            {
                'username': 'manager',
                'email': 'manager@cargo-ms.com',
                'password': 'manager123',
                'first_name': 'John',
                'last_name': 'Manager',
                'role': 'branch_manager',
                'branch': branches[0] if branches else None,
            },
            {
                'username': 'officer',
                'email': 'officer@cargo-ms.com',
                'password': 'officer123',
                'first_name': 'Jane',
                'last_name': 'Officer',
                'role': 'booking_officer',
                'branch': branches[0] if branches else None,
            },
            {
                'username': 'driver',
                'email': 'driver@cargo-ms.com',
                'password': 'driver123',
                'first_name': 'Mike',
                'last_name': 'Driver',
                'role': 'driver',
                'branch': branches[0] if branches else None,
            },
            {
                'username': 'warehouse',
                'email': 'warehouse@cargo-ms.com',
                'password': 'warehouse123',
                'first_name': 'Sam',
                'last_name': 'Warehouse',
                'role': 'warehouse_officer',
                'branch': branches[0] if branches else None,
            },
        ]
        
        for user_data in users_data:
            if not User.objects.filter(username=user_data['username']).exists():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name'],
                    is_active=True,
                )
                
                # Assign role
                role = Role.objects.filter(name=user_data['role']).first()
                if role:
                    user.role = role
                    user.save()
                
                # Assign branch
                if user_data['branch']:
                    user.branch = user_data['branch']
                    user.save()
                
                # Assign organization
                user.organization = organization
                user.save()
                
                self.stdout.write(f'  ✓ Created user: {user_data["username"]} ({user_data["role"]})')
                self.stdout.write(f'    → Password: {user_data["password"]}')
            else:
                self.stdout.write(f'  → User exists: {user_data["username"]}')

    def seed_shipments(self, organization, customers, branches):
        """Create test shipments spread across months for chart data"""
        self.stdout.write('Creating shipments for chart data...')
        
        if not customers or not branches:
            self.stdout.write('  → Skipping shipment seeding (no customers or branches)')
            return
        
        # Get admin user as creator
        admin_user = User.objects.filter(username='admin').first()
        
        # Generate shipments spread across the last 6 months
        from datetime import timedelta
        today = timezone.now().date()
        
        # Monthly shipment counts to simulate realistic data
        monthly_targets = {
            0: 820,  # Current month
            1: 910,  # 1 month ago
            2: 875,  # 2 months ago
            3: 1005, # 3 months ago
            4: 1120, # 4 months ago
            5: 1248, # 5 months ago
        }
        
        shipment_count = 0
        for months_ago, target_count in monthly_targets.items():
            month_date = today - timedelta(days=30 * months_ago)
            
            for i in range(target_count):
                # Randomly select customer and branch
                customer = customers[i % len(customers)]
                origin_branch = branches[i % len(branches)]
                dest_branch = branches[(i + 1) % len(branches)]
                
                # Generate tracking ID
                tracking_id = f'SHN-TZ-{month_date.year}-{1000 + shipment_count + i:06d}'
                booking_number = f'BOOK-{month_date.year}-{1000 + shipment_count + i:06d}'
                
                # Random status distribution
                import random
                statuses = ['booked', 'in_transit', 'delivered', 'in_warehouse', 'ready_for_delivery']
                status = random.choice(statuses)
                
                # Create shipment with date in the target month
                created_at = month_date.replace(day=random.randint(1, 28))
                
                shipment, created = Shipment.objects.get_or_create(
                    tracking_id=tracking_id,
                    defaults={
                        'organization': organization,
                        'booking_number': booking_number,
                        'customer': customer,
                        'created_by': admin_user,
                        'sender_name': customer.full_name or 'Sender Name',
                        'sender_phone': customer.phone or '+255 123 4567',
                        'sender_city': origin_branch.city,
                        'receiver_name': f'Receiver {i}',
                        'receiver_phone': '+255 765 4321',
                        'receiver_city': dest_branch.city,
                        'origin_branch': origin_branch,
                        'destination_branch': dest_branch,
                        'origin': origin_branch.city,
                        'destination': dest_branch.city,
                        'cargo_type': 'general',
                        'num_packages': random.randint(1, 10),
                        'actual_weight': Decimal(str(random.uniform(1, 100))),
                        'declared_value': Decimal(str(random.uniform(100, 10000))),
                        'status': status,
                        'created_at': created_at,
                    }
                )
                
                if created:
                    shipment_count += 1
        
        self.stdout.write(f'  ✓ Created {shipment_count} shipments across 6 months')
