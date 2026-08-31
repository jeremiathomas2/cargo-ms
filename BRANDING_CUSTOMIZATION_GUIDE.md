# Cargo Management System - Branding & Customization Guide

This guide explains how to customize the login page, tracking page, and other UI elements without modifying code.

---

## Quick Start

The system supports both **code-based** and **database-based** customization:

1. **Quick colors** → Edit CSS in template files
2. **Persistent colors** → Add to Django settings
3. **Dynamic colors** → Create database settings model

---

## Color Palette

### Current Colors (Default)

| Purpose | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary Branding | Navy | `#0B0524` | Left panel background |
| Action Buttons | Orange | `#D96A16` | Sign In, Track buttons |
| Hover States | Blue | `#38AEF2` | Button hover effect |
| Success | Green | `#1DA36B` | Status indicators |
| Error | Red | `#E5484D` | Error messages |
| Secondary | Purple | `#6D5BD0` | Accent elements |
| Light Mode BG | White | `#FFFFFF` | Light background |
| Dark Mode BG | Dark Navy | `#0A0620` | Dark background |

### Where to Change

#### Option 1: In Template CSS (Quickest)

File: `templates/auth/login.html`

Find the `<style>` section at the top:

```css
:root {
    --navy: #0B0524;      /* Change here for branding panel */
    --orange: #D96A16;    /* Change here for buttons */
    --blue: #38AEF2;      /* Change here for hover states */
    --success: #1DA36B;   /* Change here for success colors */
    --danger: #E5484D;    /* Change here for error colors */
}
```

**Example**: To change button color to teal:
```css
:root {
    --orange: #17A697;  /* Teal button color */
}
```

#### Option 2: In Django Settings (Recommended)

Create a `settings/branding.py` file:

```python
# cargo_ms/settings/branding.py

BRANDING = {
    'PRIMARY_COLOR': '#0B0524',      # Navy branding panel
    'SECONDARY_COLOR': '#D96A16',    # Orange action buttons
    'ACCENT_COLOR': '#38AEF2',       # Blue hover states
    'SUCCESS_COLOR': '#1DA36B',      # Green success
    'ERROR_COLOR': '#E5484D',        # Red errors
    'PURPLE_COLOR': '#6D5BD0',       # Purple accents
    
    # Logo / Branding
    'LOGO_EMOJI': '🚚',
    'COMPANY_NAME': 'Cargo Management & Logistics',
    'COMPANY_TAGLINE': 'Manage cargo. Track transportation. Deliver with confidence.',
    
    # Tracking Page
    'TRACKING_TITLE': 'Track Your Cargo',
    'TRACKING_DESCRIPTION': 'Enter your tracking number to see real-time updates on your shipment.',
    
    # Login Page
    'LOGIN_TITLE': 'Welcome Back',
    'LOGIN_DESCRIPTION': 'Sign in to your account to continue.',
    'SIGN_IN_TEXT': 'Sign In',
    'TRACK_CARGO_TEXT': 'Track Your Cargo',
    
    # Footer
    'SECURITY_MESSAGE': 'Your credentials are encrypted and never shared.',
    'COOKIE_NOTICE': 'This site uses HTTPS for secure communication.',
}
```

Then in `cargo_ms/settings/__init__.py`:

```python
from .branding import BRANDING
```

#### Option 3: Database Settings (Most Flexible)

Create a database model to store branding settings:

```python
# saas_config/models.py - Add to existing OrganizationSetting

class OrganizationSetting(models.Model):
    # ... existing fields ...
    
    # Branding
    primary_color = models.CharField(max_length=7, default='#0B0524')
    secondary_color = models.CharField(max_length=7, default='#D96A16')
    accent_color = models.CharField(max_length=7, default='#38AEF2')
    company_name = models.CharField(max_length=200, default='Cargo Management & Logistics')
    company_tagline = models.CharField(max_length=500, default='Manage cargo. Track transportation. Deliver with confidence.')
    logo_text = models.CharField(max_length=1, default='🚚')
    
    class Meta:
        verbose_name = "Organization Settings"
        verbose_name_plural = "Organization Settings"
```

Then create a template tag to inject colors dynamically.

---

## Customizing Different Sections

### 1. Branding Panel (Left Side)

**Files affected:**
- `templates/auth/login.html` (lines 280-350)

**Elements to customize:**

```html
<!-- Logo/Icon -->
<div class="w-20 h-20 bg-gradient-to-br from-[#D96A16] to-[#E07B2C]">
    🚚  <!-- Change emoji here -->
</div>

<!-- Title -->
<h1 class="text-4xl font-black text-white">
    Cargo Management<br>& Logistics
</h1>

<!-- Tagline -->
<p class="text-lg text-gray-300">
    Manage cargo. Track transportation. Deliver with confidence.
</p>

<!-- Cargo Flow Animation -->
<div class="cargo-flow">
    <div class="cargo-item">📦 Cargo</div>
    <div class="arrow">→</div>
    <div class="cargo-item">🏭 Warehouse</div>
    <div class="arrow">→</div>
    <div class="cargo-item">🚛 Transport</div>
    <div class="arrow">→</div>
    <div class="cargo-item">🎯 Deliver</div>
</div>
```

### 2. Login Form (Right Side)

**Files affected:**
- `templates/auth/login.html` (lines 360-500)

**Elements to customize:**

```html
<!-- Form Title -->
<h2 class="text-3xl font-black">Welcome Back</h2>
<p>Sign in to your account to continue.</p>

<!-- Input Fields -->
<label>Email or Username</label>
<input placeholder="Enter your email or username" />

<!-- Button -->
<button class="btn-primary">SIGN IN</button>

<!-- Secondary Button -->
<button class="btn-secondary">TRACK YOUR CARGO</button>
```

### 3. Public Tracking Page

**Files affected:**
- `templates/auth/track_cargo.html` (lines 200-300)

**Elements to customize:**

```html
<!-- Page Title -->
<h1 class="text-5xl font-black">Track Your Cargo</h1>
<p>Enter your tracking number to see real-time updates on your shipment.</p>

<!-- Search Label -->
<label>Tracking Number</label>
<input placeholder="e.g. CMS-TZ-2026-00001245" />

<!-- Timeline Title -->
<h3 class="text-xl font-black">Shipment Journey</h3>
```

---

## Color Customization Examples

### Example 1: Green Corporate Branding

```css
:root {
    --navy: #1B5E20;      /* Dark green instead of navy */
    --orange: #00A651;    /* Bright green buttons */
    --blue: #00D084;      /* Light green hover */
}
```

### Example 2: Blue Professional Theme

```css
:root {
    --navy: #003A70;      /* Dark blue branding */
    --orange: #0066CC;    /* Professional blue */
    --blue: #0099FF;      /* Light blue hover */
}
```

### Example 3: Red/Pink Modern

```css
:root {
    --navy: #5A0000;      /* Deep red branding */
    --orange: #E63946;    /* Red buttons */
    --blue: #F4A6C1;      /* Pink hover */
}
```

### Example 4: Purple Premium

```css
:root {
    --navy: #2D1B69;      /* Deep purple */
    --orange: #6D28D9;    /* Purple action */
    --blue: #A78BFA;      /* Light purple hover */
}
```

---

## Font Customization

### Current Font
**Nunito Sans** (Google Fonts)
- Weights: 400, 500, 600, 700, 800, 900
- Styles: Normal

### To Change Font

In `templates/auth/login.html` `<head>`:

```html
<!-- Remove/Comment out current font -->
<!-- <link href="https://fonts.googleapis.com/css2?family=Nunito+Sans:..." rel="stylesheet"> -->

<!-- Add new font -->
<link href="https://fonts.googleapis.com/css2?family=YOUR_FONT:wght@400;600;700&display=swap" rel="stylesheet">
```

Update CSS:
```css
html, body {
    font-family: 'YOUR_FONT', system-ui, sans-serif;
}
```

**Popular alternatives:**
- Inter (Modern, clean)
- Poppins (Trendy, friendly)
- Roboto (Professional, neutral)
- Montserrat (Bold, geometric)

---

## Animation Customization

### Fade-In Duration

File: `templates/auth/login.html` CSS

```css
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

.animate-fade-in {
    animation: fadeIn 0.8s ease-out;  /* Change 0.8s to your value */
}
```

### Slide Duration

```css
@keyframes slideInLeft {
    from {
        opacity: 0;
        transform: translateX(-30px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

.animate-slide-in {
    animation: slideInLeft 0.6s ease-out;  /* Change 0.6s to your value */
}
```

### Disable Animations (for accessibility)

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Background Customization

### Change Gradient Colors

File: `templates/auth/login.html` CSS

```css
/* Left panel gradient */
<div class="bg-gradient-to-br from-[#0B0524] via-[#1E1548] to-[#0B0524]">
    <!-- Change #0B0524 and #1E1548 to your colors -->
</div>

/* Dark mode gradient */
<div class="bg-gradient-to-br from-white via-gray-50 to-blue-50">
    <!-- Change to your light mode gradient -->
</div>
```

### Add Custom Background Image

```css
.left-panel {
    background-image: url('/static/images/cargo-pattern.png');
    background-size: cover;
    background-position: center;
}
```

---

## Dark Mode Customization

### Light Mode Colors

Update in CSS `:root`:
```css
html {
    @apply bg-white text-gray-900;
}
```

### Dark Mode Colors

Update in CSS `html.dark`:
```css
html.dark {
    @apply bg-[#0A0620] text-white;
}
```

### Individual Element Dark Styling

```css
/* Light mode */
.form-input {
    background: white;
    color: #111827;
}

/* Dark mode */
html.dark .form-input {
    background: #1A1240;
    color: white;
}
```

---

## Logo & Icon Customization

### Current Setup
Emoji logo in template: `🚚`

### Change to Image

```html
<!-- Replace emoji -->
<div class="w-20 h-20 rounded-2xl flex items-center justify-center shadow-lg">
    <img src="{% static 'images/logo.png' %}" alt="Logo" class="w-full h-full">
</div>
```

### Change Emoji

Simply edit: `🚚` → `📦` or `🏭` or `🌍` etc.

---

## Typography Customization

### Button Text Size

```css
.btn-primary {
    font-size: 1rem;  /* Change size */
    font-weight: 600; /* Change weight */
    text-transform: uppercase; /* Change styling */
}
```

### Form Labels

```css
label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #333;
}
```

---

## Spacing & Layout

### Form Width

```css
.max-w-md {
    max-width: 28rem;  /* 448px - change for wider form */
}
```

### Panel Padding

```css
/* Left panel padding */
.p-12 {
    padding: 3rem;  /* Change for more/less space */
}

/* Right panel padding */
.p-6 { padding: 1.5rem; }
```

---

## Mobile Customization

### Hide Elements on Mobile

```css
@media (max-width: 768px) {
    .hidden-mobile {
        display: none;
    }
}
```

### Show Elements on Mobile

```css
@media (max-width: 768px) {
    .mobile-only {
        display: block;
    }
}
```

---

## Accessibility Customization

### Focus States

```css
input:focus {
    outline: 2px solid #D96A16;
    outline-offset: 2px;
}
```

### Color Contrast

Ensure WCAG AA compliance (4.5:1 ratio):
- Text on light background
- Text on dark background
- Button text on button

### Motion Preferences

```css
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

---

## Testing Custom Colors

### Before & After

1. Take screenshot of current login page
2. Update CSS variables
3. Hard refresh browser (Ctrl+Shift+R)
4. Compare with original

### Accessibility Check

Use tools:
- WebAIM Contrast Checker
- WAVE Accessibility Tool
- Lighthouse (Chrome DevTools)

### Cross-Browser Testing

Test on:
- Chrome (Desktop & Mobile)
- Firefox (Desktop & Mobile)
- Safari (Desktop & Mobile)
- Edge

---

## Reverting Changes

### Quick Reset

Find the style section and reset to:

```css
:root {
    --navy: #0B0524;
    --orange: #D96A16;
    --blue: #38AEF2;
    --success: #1DA36B;
    --danger: #E5484D;
}
```

### Full Reset

```bash
# Restore from git
git checkout -- templates/auth/login.html
```

---

## Production Deployment

When going to production:

1. **Test colors** thoroughly
2. **Check contrast** for accessibility
3. **Test on mobile** thoroughly
4. **Test in all browsers**
5. **Minify CSS** for production
6. **Cache bust** static files
7. **Monitor for errors** in browser console

---

## Support

If you encounter issues:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+Shift+R)
3. Check browser console for errors (F12)
4. Verify color hex codes are valid (#RRGGBB format)
5. Test in incognito/private mode

---

## Resources

- [Color Picker](https://htmlcolorcodes.com/)
- [Google Fonts](https://fonts.google.com/)
- [Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [CSS Gradients](https://cssgradient.io/)
- [Emoji Picker](https://emoji-pedia.org/)

