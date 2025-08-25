# Mikrotik Integration Guide

This guide explains how to integrate the IntaSend payment system with Mikrotik hotspot for automatic WiFi access after payment.

## Overview

The Mikrotik integration provides a seamless payment-to-access flow:

1. **User connects to WiFi** → Redirected to login page
2. **Selects package** → Chooses duration and price
3. **Enters phone number** → M-Pesa STK push initiated
4. **Completes payment** → IntaSend confirms payment
5. **Auto-login** → User automatically connected to WiFi
6. **Package activation** → Access granted for selected duration

## Files

### 1. Basic Login Page
- **File**: `static/mikrotik-login.html`
- **Use Case**: Simple integration with basic client detection
- **Features**: Package selection, phone input, payment processing

### 2. Enhanced Login Page
- **File**: `static/mikrotik-login-enhanced.html`
- **Use Case**: Advanced integration with detailed client information
- **Features**: Client IP/MAC detection, debug logging, enhanced Mikrotik integration

## Mikrotik Login Pages

The system provides two pre-configured login pages that can be served directly from Django to avoid CORS issues:

### Available Login Pages

1. **Basic Login Page**: `/api/payments/mikrotik-login/`
   - Simple package selection and payment flow
   - Basic client information detection
   - Suitable for most Mikrotik setups

2. **Enhanced Login Page**: `/api/payments/mikrotik-login-enhanced/`
   - Advanced client information detection
   - Debug logging and detailed error handling
   - Better integration with Mikrotik parameters

### Accessing the Login Pages

Instead of opening the HTML files directly in your browser (which causes CORS issues), access them through Django:

```bash
# Basic login page
http://yourdomain.com/api/payments/mikrotik-login/

# Enhanced login page  
http://yourdomain.com/api/payments/mikrotik-login-enhanced/
```

### Configuration

The login pages are automatically configured with:
- Your public API key
- Relative API paths (no CORS issues)
- Default router ID (update in the view if needed)

### Customization

To customize the login pages:
1. Edit the HTML files in the `static/` directory
2. Update the `mikrotik_login_page()` and `mikrotik_login_enhanced()` views in `payments/views.py`
3. Restart Django to see changes

## Setup Instructions

### Step 1: Configure the Login Page

Update the configuration variables in your chosen HTML file:

```javascript
// Configuration - Update these values
const API_BASE_URL = 'https://yourdomain.com/api'; // Your Django API domain
const ROUTER_ID = 1; // Your router ID from the database
const JWT_TOKEN = 'your_jwt_token'; // Valid JWT token for API access
const SHOW_DEBUG = true; // Set to false in production
```

**Required Updates:**
- `API_BASE_URL`: Your Django server domain (e.g., `https://api.guntu.net`)
- `ROUTER_ID`: The router ID from your database
- `JWT_TOKEN`: A valid JWT token with payment permissions

### Step 2: Upload to Mikrotik

#### Option A: Direct File Upload
1. Access your Mikrotik router via WinBox or SSH
2. Go to **Files** → **Upload** the HTML file
3. Note the file path (e.g., `/mikrotik-login.html`)

#### Option B: Web Server Hosting
1. Host the HTML file on your web server
2. Ensure it's accessible via HTTPS
3. Note the full URL

### Step 3: Configure Mikrotik Hotspot

#### Basic Hotspot Configuration
```bash
# Enable hotspot
/ip hotspot setup

# Set hotspot profile
/ip hotspot profile set [find name=default] \
    hotspot-address=192.168.1.0/24 \
    dns-name=hotspot.guntu.net \
    login-cookie=hotspot

# Configure hotspot server
/ip hotspot server set [find] \
    address=192.168.1.1 \
    profile=default \
    idle-timeout=5m \
    keepalive-timeout=2m \
    login-timeout=1m
```

#### Custom Login Page Configuration
```bash
# Set custom login page
/ip hotspot profile set [find name=default] \
    login-page=/mikrotik-login.html

# Or for external hosting
/ip hotspot profile set [find name=default] \
    login-page=https://yourdomain.com/mikrotik-login.html
```

#### Advanced Hotspot Settings
```bash
# Configure user profiles
/ip hotspot user profile add name=1hour rate-limit=1M/1M
/ip hotspot user profile add name=3hours rate-limit=2M/2M
/ip hotspot user profile add name=24hours rate-limit=5M/5M

# Set session timeout
/ip hotspot user profile set [find name=1hour] session-timeout=1:00:00
/ip hotspot user profile set [find name=3hours] session-timeout=3:00:00
/ip hotspot user profile set [find name=24hours] session-timeout=24:00:00
```

### Step 4: Configure DNS and Network

#### DNS Configuration
```bash
# Add DNS entry for hotspot
/ip dns static add name=hotspot.guntu.net address=192.168.1.1

# Configure DNS servers for clients
/ip hotspot profile set [find name=default] \
    dns-server=8.8.8.8,8.8.4.4
```

#### Network Configuration
```bash
# Configure hotspot interface
/interface bridge add name=hotspot-bridge
/ip address add address=192.168.1.1/24 interface=hotspot-bridge

# Add wireless interface to bridge
/interface bridge port add bridge=hotspot-bridge interface=wlan1
```

## Client Information Detection

### Automatic Detection Methods

The enhanced login page automatically detects client information:

#### 1. URL Parameters
Mikrotik can pass client information via URL parameters:

```
https://hotspot.guntu.net/login?ip=192.168.1.100&mac=AA:BB:CC:DD:EE:FF&router=AP1
```

#### 2. Mikrotik Variables
Common Mikrotik variables that can be passed:

| Variable | Description | Example |
|----------|-------------|---------|
| `ip` | Client IP address | `192.168.1.100` |
| `mac` | Client MAC address | `AA:BB:CC:DD:EE:FF` |
| `router` | Router/AP name | `AP1` |
| `ssid` | WiFi network name | `Guntu_WiFi` |
| `user` | Username (if any) | `guest` |

#### 3. Custom URL Configuration
Configure Mikrotik to pass additional parameters:

```bash
# Custom login URL with parameters
/ip hotspot profile set [find name=default] \
    login-page="https://yourdomain.com/mikrotik-login.html?ip=${ip}&mac=${mac}&router=${router_name}"
```

### Fallback Detection

If Mikrotik doesn't pass parameters, the system uses fallbacks:

```javascript
// Fallback IP detection
function detectLocalIP() {
    // Returns placeholder IP if detection fails
    return '192.168.1.100';
}

// Fallback MAC detection
function detectLocalMAC() {
    // Returns placeholder MAC if detection fails
    return 'AA:BB:CC:DD:EE:FF';
}
```

## Package Configuration

### Default Packages

The login page comes with three default packages:

| Package ID | Duration | Price | Description |
|------------|----------|-------|-------------|
| 1 | 1 Hour | KES 10.00 | Fast internet for 1 hour |
| 2 | 3 Hours | KES 25.00 | Extended internet access |
| 3 | 24 Hours | KES 50.00 | Full day internet access |

### Customizing Packages

To customize packages, update the HTML:

```html
<div class="package-option" data-package-id="1" data-price="15.00" data-duration="2">
    <div class="package-name">2 Hours Package</div>
    <div class="package-details">Extended internet access for 2 hours</div>
    <div class="package-price">KES 15.00</div>
</div>
```

**Important**: Package IDs must match those in your Django database.

### Package-Database Synchronization

Ensure your Django packages match the login page:

```python
# Example package creation
from routers.models import Package, Router

router = Router.objects.get(id=1)
Package.objects.create(
    router=router,
    name="1 Hour Package",
    package_type="hourly",
    duration_hours=1,
    price=10.00,
    speed_mbps=10,
    is_active=True
)
```

## Payment Flow Integration

### 1. Payment Initiation

When user clicks "Pay with M-Pesa":

```javascript
const paymentData = {
    router_id: ROUTER_ID,
    package_id: selectedPackage.id,
    phone_number: phoneNumber,
    amount: selectedPackage.price,
    mac_address: clientInfo.mac,
    ip_address: clientInfo.ip
};

// Call IntaSend API
const response = await fetch(`${API_BASE_URL}/payments/intasend/initiate/`, {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${JWT_TOKEN}`,
        'Content-Type': 'application/json'
    },
    body: JSON.stringify(paymentData)
});
```

### 2. Status Polling

After payment initiation, the system polls for status:

```javascript
async function pollPaymentStatus() {
    // Check payment status every 3 seconds
    const response = await fetch(`${API_BASE_URL}/payments/intasend/${currentPayment.id}/check-status/`);
    
    if (result.status === 'completed') {
        // Payment successful - auto-login to Mikrotik
        autoLoginToMikrotik();
    } else if (result.status === 'failed') {
        // Payment failed - show error
        showStatus('Payment failed. Please try again.', 'error');
    } else {
        // Still processing - continue polling
        setTimeout(pollPaymentStatus, 3000);
    }
}
```

### 3. Auto-Login

Upon successful payment:

```javascript
function autoLoginToMikrotik() {
    const currentUrl = window.location.href;
    const loginUrl = new URL(currentUrl);
    
    // Add Mikrotik authentication parameters
    loginUrl.searchParams.set('dst', '/');
    loginUrl.searchParams.set('popup', 'true');
    loginUrl.searchParams.set('username', 'guest');
    loginUrl.searchParams.set('password', 'guest');
    
    // Redirect to complete login
    window.location.href = loginUrl.toString();
}
```

## Security Considerations

### 1. JWT Token Management

**Never expose JWT tokens in client-side code in production!**

Instead, use one of these approaches:

#### Option A: Server-Side Token Generation
```python
# Create a view that generates temporary tokens
@api_view(['POST'])
def generate_hotspot_token(request):
    # Validate request (e.g., check if from Mikrotik)
    token = AccessToken.for_user(request.user)
    return Response({'token': str(token)})
```

#### Option B: Session-Based Authentication
```python
# Use Django sessions instead of JWT
@api_view(['POST'])
def initiate_hotspot_payment(request):
    if request.session.get('hotspot_authenticated'):
        # Process payment
        pass
```

#### Option C: IP-Based Authentication
```python
# Allow requests from Mikrotik IP range
class MikrotikAuthentication(BaseAuthentication):
    def authenticate(self, request):
        client_ip = get_client_ip(request)
        if client_ip.startswith('192.168.1.'):
            return (AnonymousUser(), None)
        return None
```

### 2. HTTPS Requirements

- **Always use HTTPS** for production
- **Valid SSL certificate** required
- **Secure cookies** for session management

### 3. Rate Limiting

Implement rate limiting to prevent abuse:

```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/m', method='POST')
@api_view(['POST'])
def initiate_intasend_payment(request):
    # Payment logic
    pass
```

## Testing and Debugging

### 1. Debug Mode

Enable debug mode during development:

```javascript
const SHOW_DEBUG = true; // Set to false in production
```

Debug information includes:
- Client IP/MAC detection
- API request/response data
- Payment flow status
- Error details

### 2. Console Logging

Check browser console for detailed logs:

```javascript
console.log('Payment initiated:', paymentData);
console.log('API response:', result);
console.log('Client info:', clientInfo);
```

### 3. Network Tab

Monitor API calls in browser DevTools:
- Request payloads
- Response data
- HTTP status codes
- Headers

### 4. Common Issues

#### Payment Not Initiating
- Check JWT token validity
- Verify API endpoint URL
- Check browser console for errors
- Ensure CORS is configured

#### Client Info Not Detected
- Verify Mikrotik URL parameters
- Check fallback values
- Enable debug mode
- Review network configuration

#### Auto-Login Not Working
- Check Mikrotik login parameters
- Verify redirect URL format
- Test with manual login
- Review hotspot configuration

## Production Deployment

### 1. File Optimization

- **Minify CSS/JS** for faster loading
- **Compress images** for bandwidth savings
- **Enable gzip** on web server
- **Use CDN** for static assets

### 2. Security Hardening

- **Disable debug mode** (`SHOW_DEBUG = false`)
- **Use secure JWT tokens**
- **Implement rate limiting**
- **Enable HTTPS only**

### 3. Monitoring

- **Log payment attempts**
- **Monitor API usage**
- **Track success rates**
- **Alert on failures**

### 4. Backup and Recovery

- **Regular backups** of configuration
- **Version control** for login pages
- **Rollback procedures** for updates
- **Disaster recovery** plan

## Advanced Features

### 1. Custom Branding

Update the login page with your branding:

```css
.logo {
    background: linear-gradient(135deg, #your-color1, #your-color2);
}

.pay-button {
    background: linear-gradient(135deg, #your-primary, #your-secondary);
}
```

### 2. Multi-Language Support

Add language selection:

```javascript
const languages = {
    en: { title: 'WiFi Login', subtitle: 'Choose a package...' },
    sw: { title: 'WiFi Ingia', subtitle: 'Chagua paketi...' }
};

function setLanguage(lang) {
    document.getElementById('title').textContent = languages[lang].title;
    document.getElementById('subtitle').textContent = languages[lang].subtitle;
}
```

### 3. Analytics Integration

Track user behavior:

```javascript
// Google Analytics
gtag('event', 'payment_initiated', {
    package_id: selectedPackage.id,
    amount: selectedPackage.price
});

// Custom tracking
fetch('/api/analytics/track', {
    method: 'POST',
    body: JSON.stringify({
        action: 'package_selected',
        package: selectedPackage
    })
});
```

## Support and Troubleshooting

### 1. Common Questions

**Q: How do I change package prices?**
A: Update both the HTML file and Django database to match.

**Q: Can I add more payment methods?**
A: Yes, extend the payment logic to support other providers.

**Q: How do I customize the design?**
A: Modify the CSS styles in the HTML file.

### 2. Getting Help

- **Documentation**: Check this guide and API docs
- **Debug Mode**: Enable for detailed error information
- **Console Logs**: Check browser developer tools
- **API Testing**: Test endpoints with Postman/cURL

### 3. Updates and Maintenance

- **Regular Updates**: Keep packages and prices current
- **Security Patches**: Monitor for security updates
- **Performance Monitoring**: Track loading times and success rates
- **User Feedback**: Collect and address user concerns

## Conclusion

The Mikrotik integration provides a complete payment-to-access solution for WiFi hotspots. By following this guide, you can:

1. **Deploy** the login page on your Mikrotik router
2. **Configure** packages and pricing
3. **Integrate** with the IntaSend payment system
4. **Automate** user access after payment
5. **Monitor** and maintain the system

For additional support or customization, refer to the API documentation and contact the development team.
