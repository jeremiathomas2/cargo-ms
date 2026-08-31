# Management Commands Documentation

## Seed Data Command

The `seed_data` management command initializes the Cargo Management System with essential data including roles, permissions, organizations, branches, and customers.

### Usage

```bash
python manage.py seed_data
```

### Options

#### `--clear`
Clears existing data before seeding. **Use with caution!**

```bash
python manage.py seed_data --clear
```

### What Gets Seeded

1. **Roles (15 total)**
   - Super Administrator
   - System Administrator
   - Head Office Manager
   - Branch Manager
   - Booking Officer
   - Customer Service Officer
   - Warehouse Officer
   - Dispatch Officer
   - Transport Manager
   - Driver
   - Delivery Officer
   - Accountant
   - Finance Manager
   - Auditor
   - Customer

2. **Permissions (38 total)**
   - Module-action pairs covering: cargo, package, warehouse, vehicle, driver, GPS, payment, invoice, document, report, user, settings, and audit

3. **Organization**
   - Cargo Management Solutions (Enterprise plan)

4. **Superuser Account**
   - Username: `admin`
   - Password: `admin123`
   - Email: `admin@cargo-ms.com`

5. **Branches (3 total)**
   - Dar es Salaam Head Office (HQ-DES) - Headquarters
   - Arusha Branch (BR-ARU)
   - Mbeya Branch (BR-MBE)

6. **Test Users (4 total)**
   - `manager` (Branch Manager) - Password: `manager123`
   - `officer` (Booking Officer) - Password: `officer123`
   - `driver` (Driver) - Password: `driver123`
   - `warehouse` (Warehouse Officer) - Password: `warehouse123`

7. **Customers (4 total)**
   - ABC Trading Ltd (Company)
   - XYZ Logistics (Company)
   - John Doe (Individual)
   - Jane Smith (Individual)

### Example Workflow

1. **First Time Setup:**
   ```bash
   # Run migrations
   python manage.py migrate
   
   # Seed initial data
   python manage.py seed_data
   ```

2. **Reset Database:**
   ```bash
   # Clear existing data and reseed
   python manage.py seed_data --clear
   ```

### Test Credentials

After seeding, you can use these credentials to test the system:

| Username | Role | Password | Email |
|----------|------|----------|-------|
| admin | Superuser | admin123 | admin@cargo-ms.com |
| manager | Branch Manager | manager123 | manager@cargo-ms.com |
| officer | Booking Officer | officer123 | officer@cargo-ms.com |
| driver | Driver | driver123 | driver@cargo-ms.com |
| warehouse | Warehouse Officer | warehouse123 | warehouse@cargo-ms.com |

### Implementation Details

The command is implemented in `core/management/commands/seed_data.py` with the following methods:

- `seed_roles_and_permissions()` - Creates system roles and granular permissions
- `seed_organizations()` - Creates the main organization
- `seed_admin_user()` - Creates the superuser account
- `seed_branches()` - Creates branch locations with settings
- `seed_customers()` - Creates test customers with addresses and contacts
- `seed_users()` - Creates test users with assigned roles and branches

### Security Notes

⚠️ **Important:** The test passwords should be changed in production. Never commit production passwords or sensitive data to version control.

For production deployment:
1. Change all test account passwords
2. Consider removing test data or using environment-based configuration
3. Implement proper user provisioning workflows
