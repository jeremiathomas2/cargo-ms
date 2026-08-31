# Login & Authentication System - Implementation Guide

## Overview

The Cargo Management System features a professional two-section desktop login layout with full mobile responsiveness, theme support, and public cargo tracking capabilities.

---

## Architecture

### Components

1. **Login Page** (`templates/auth/login.html`)
   - Two-section desktop layout (branding panel + login form)
   - Mobile responsive single-column layout
   - Light/Dark theme support
   - Password visibility toggle
   - Remember me functionality
   - Secure token-based authentication

2. **Public Cargo Tracking** (`templates/auth/track_cargo.html`)
   - No login required
   - Real-time shipment tracking
   - Tracking timeline visualization
   - Multiple display formats (mobile/desktop)
   - Theme support

3. **Authentication Views** (`accounts/views.py`)
   - `EnhancedLoginView` - Main login endpoint
   - `PublicTrackingView` - Public cargo tracking page

### Design Features

#### Color Scheme
- **Navy Background**: `#0B0524` (Branding panel)
- **Primary Orange**: `#D96A16` (Buttons, accents)
- **Secondary Blue**: `#38AEF2` (Hover states)
- **Success Green**: `#1DA36B` (Status indicators)
- **White Background**: Login form (light mode)
- **Dark Navy**: `#0A0620` (Dark mode)

#### Animations
- Fade-in entrance: 0.8s smooth animation
- Slide-in left branding panel: 0.6s ease-out
- Subtle float background elements: Infinite 6s cycle
- Cargo flow sequence: Staggered fade-in
- Smooth theme transitions: 0.3s ease

#### Responsive Breakpoints
- **Desktop**: Two-column layout (hidden on mobile)
- **Tablet (768px)**: Responsive grid adjustments
- **Mobile**: Single-column stacked layout

---

## URL Structure

### Authentication Routes

```
/accounts/login/              → Login page (enhanced)
/accounts/track/              → Public cargo tracking
/accounts/password-reset/     → Password reset request
/accounts/register/           → User registration
/accounts/profile/            → User profile (authenticated)
```

### API Endpoints (for tracking)

```
GET  /api/public-tracking/{tracking_number}/
     ├─ Response: Shipment details with events
     └─ Access: Public (no authentication required)
```

---

## Usage

### Standard Login Flow

```
1. User navigates to /accounts/login/
2. Enters email/username and password
3. System validates credentials
4. On success:
   - Token is generated
   - Session is created
   - User is redirected to dashboard
   - Activity is logged
5. On failure:
   - Generic error message (security best practice)
   - IP address is recorded
```

### Public Tracking Flow

```
1. User navigates to /accounts/track/
2. Enters tracking number
3. System queries public tracking API
4. Results displayed with timeline
5. No authentication required
```

---

## Theme Customization

### Light Mode (Default)
```css
Background: #FFFFFF
Text: #111827
Card: #FFFFFF
Border: #E5E7EB
Input: White
```

### Dark Mode
```css
Background: #0A0620
Text: #FFFFFF
Card: #150E33
Border: #2D2649
Input: #1A1240
```

### Theme Switching

Users can toggle theme using the moon/sun button in top-right corner:

```javascript
// Toggle theme
localStorage.setItem('theme', darkMode ? 'dark' : 'light');

// Apply theme
document.documentElement.className = darkMode ? 'dark' : '';
```

The system uses:
- **localStorage** for persistence
- **prefers-color-scheme** media query for system preference detection
- Alpine.js for reactive state management

---

## Security Implementation

### Protection Measures

1. **Password Security**
   - Password field uses dots masking
   - Eye icon for visibility toggle
   - Password change support
   - Password reset via email

2. **Session Management**
   - CSRF token validation
   - Secure HttpOnly cookies (production)
   - Session timeout (configurable)
   - User activity logging
   - IP address tracking
   - User agent logging

3. **Authentication**
   - Token-based JWT authentication
   - Secure login endpoint
   - Generic error messages (no account existence reveal)
   - Login throttling (recommended)
   - Account lockout (recommended)
   - Two-factor authentication (optional)

4. **Data Protection**
   - HTTPS only (production)
   - No password storage in frontend
   - Secure CSRF token handling
   - No sensitive data in localStorage (except theme)

### Audit Trail

All login attempts are logged with:
- User ID / Email
- Timestamp
- IP Address
- User Agent
- Success/Failure status
- Login Source (web/api/mobile)

Access logs at: `UserActivity.objects.filter(action='login')`

---

## Customization

### Branding

To customize the branding panel:

1. **Logo/Icon**: Edit the emoji in the branding section (line ~280)
   ```html
   <div class="w-20 h-20 bg-gradient-to-br from-[#D96A16] to-[#E07B2C] 
        rounded-2xl flex items-center justify-center text-4xl shadow-lg">
       🚚  <!-- Change this emoji -->
   </div>
   ```

2. **Title & Tagline**: Edit lines ~295-310
   ```html
   <h1>Cargo Management & Logistics</h1>
   <p>Manage cargo. Track transportation. Deliver with confidence.</p>
   ```

3. **Cargo Flow**: Edit the cargo flow section (lines ~320-350)
   ```html
   📦 → 🏭 → 🚛 → 🎯
   ```

### Color Customization

Update the CSS variables in the `<style>` section (lines ~25-29):

```css
:root {
    --navy: #0B0524;        /* Change branding panel color */
    --orange: #D96A16;      /* Change primary button/accent */
    --blue: #38AEF2;        /* Change hover/secondary states */
    --success: #1DA36B;     /* Change success indicators */
    --danger: #E5484D;      /* Change error indicators */
}
```

### Button Customization

**Primary Button** (Sign In):
```css
.btn-primary {
    background: linear-gradient(135deg, #D96A16 0%, #E07B2C 100%);
    /* Modify gradient colors here */
}

.btn-primary:hover {
    background: linear-gradient(135deg, #38AEF2 0%, #2BA0DC 100%);
    /* Modify hover gradient here */
}
```

**Secondary Button** (Track Cargo):
```css
.btn-secondary {
    color: var(--orange);
    border: 2px solid var(--orange);
    /* Modify border and text color */
}
```

### Form Styling

Input focus state:
```css
.form-input:focus {
    border-color: var(--orange);
    box-shadow: 0 0 0 3px rgba(217, 106, 22, 0.1);
}
```

---

## API Integration

### Public Tracking Endpoint

**Request:**
```
GET /api/public-tracking/{tracking_number}/
Content-Type: application/json
```

**Response (200 OK):**
```json
{
  "tracking_id": "CMS-TZ-2026-00001245",
  "status": "in_transit",
  "status_display": "In Transit",
  "customer_name": "John Doe",
  "destination_city": "Dar es Salaam",
  "expected_delivery": "2026-09-05",
  "events": [
    {
      "id": "uuid",
      "status": "in_transit",
      "status_display": "In Transit",
      "created_at": "2026-08-31T14:30:00Z",
      "location": "Dar es Salaam Hub",
      "notes": "Shipment in transit",
      "icon": "🚛"
    }
  ]
}
```

**Error Response (404):**
```json
{
  "detail": "Tracking number not found."
}
```

---

## Frontend Features

### Password Toggle

The eye icon button reveals/hides password:
```javascript
togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
}
```

### Remember Me

Stores username in localStorage:
```javascript
localStorage.setItem('lastUsername', username);
localStorage.setItem('rememberMe', 'true');
```

On page load, username is restored if previously selected.

### Loading State

During login submission:
```javascript
<span x-show="!loading">Sign In</span>
<span x-show="loading">
    <span class="spinner"></span> Signing In...
</span>
```

### Error Handling

Displays only generic error messages:
```
"Invalid username or password."
```

Never reveals whether account exists or not.

---

## Mobile Optimization

### Layout Changes
- Branding panel hidden on screens < 768px
- Full-width login form on mobile
- Logo displayed inside the card
- Simplified cargo flow animation

### Touch Optimization
- Larger touch targets (44px minimum)
- Reduced animations on smaller screens
- Optimized form inputs for mobile keyboards
- Single-column layout

### Performance
- No JavaScript blocking rendering
- Lazy loading of non-critical assets
- Minimal CSS for mobile
- Fast theme switching without page reload

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile Safari 14+
- Android Chrome 90+

**Note**: The page uses:
- CSS Grid/Flexbox (all modern browsers)
- CSS custom properties
- Alpine.js for interactivity
- Fetch API
- localStorage

---

## Environment Configuration

### Required Settings

In `.env`:
```env
DEBUG=True  # Set to False in production
ALLOWED_HOSTS=localhost,127.0.0.1
SECURE_SSL_REDIRECT=False  # Set to True in production
SESSION_COOKIE_SECURE=False  # Set to True in production
CSRF_COOKIE_SECURE=False  # Set to True in production
CSRF_COOKIE_HTTPONLY=True
SESSION_COOKIE_HTTPONLY=True
```

### Production Recommendations

```env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True
```

---

## Troubleshooting

### Login Not Working

1. **Check CSRF Token**
   - Ensure Django CSRF middleware is enabled
   - Token is included in form

2. **Check User Exists**
   ```python
   from django.contrib.auth import get_user_model
   User = get_user_model()
   user = User.objects.filter(username='admin')
   ```

3. **Check Database**
   - Run migrations: `python manage.py migrate`
   - Seed data: `python manage.py seed_data`

### Theme Not Persisting

1. Check localStorage is enabled
2. Check browser privacy settings
3. Verify JavaScript is enabled

### Tracking Page Not Loading

1. Verify public tracking API endpoint exists
2. Check CORS settings if API is on different domain
3. Verify shipment data in database

### Form Validation Issues

1. Ensure `name` attributes match expected form fields
2. Check browser console for JavaScript errors
3. Verify field names: `username`, `password`

---

## Performance Tips

1. **Caching**
   - Cache branding assets
   - Use CDN for static files

2. **Optimization**
   - Minify CSS/JS in production
   - Compress images
   - Use GZIP compression

3. **Loading**
   - Defer non-critical JavaScript
   - Use CSS instead of images where possible
   - Lazy load tracking results

---

## Future Enhancements

1. **Biometric Login** (fingerprint/face)
2. **Social Login** (Google, Microsoft)
3. **OTP Login** (phone number)
4. **2FA Setup** (TOTP/SMS)
5. **Login History Dashboard**
6. **Device Management**
7. **Passwordless Login**
8. **Login Analytics**

---

## Support & Documentation

For issues or questions:
1. Check browser console for errors
2. Review Django logs
3. Verify database connectivity
4. Check user permissions
5. Review security audit trail

