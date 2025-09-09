# 📧 Official Email Addresses Mapping - Soleva Website

## Official Brand Emails

| Email Address | Purpose | Usage Context |
|---------------|---------|---------------|
| **info@solevaeg.com** | General inquiries, information requests, primary contact | Main contact email for general questions |
| **support@solevaeg.com** | Customer service, technical support, order assistance | Customer support and help |
| **sales@solevaeg.com** | Sales inquiries, bulk orders, product information | Sales-related communications |
| **business@solevaeg.com** | Partnerships, business opportunities, collaborations | B2B communications and partnerships |

---

## Complete Website Mapping

### 🔗 **Header Section**
| Location | Email Used | File Path |
|----------|------------|-----------|
| Header contact info (if displayed) | `info@solevaeg.com` | `soleva front end/src/components/AppHeader.tsx` |

### 🦶 **Footer Section**
| Location | Email Used | File Path |
|----------|------------|-----------|
| Footer contact information | `info@solevaeg.com` | `soleva front end/src/components/AppFooter.tsx` |
| Footer company description | Dynamic from `siteConfig.primary_email` | `soleva front end/src/components/AppFooter.tsx` |

### 📄 **Contact Us Page**
| Location | Email Used | File Path |
|----------|------------|-----------|
| Main contact email display | `info@solevaeg.com` | `soleva front end/src/pages/ContactPage.tsx` |
| Contact form submission endpoint | `info@solevaeg.com` | `soleva front end/src/pages/ContactPage.tsx` |

### 📜 **Legal Pages**
| Location | Email Used | File Path |
|----------|------------|-----------|
| Privacy Policy contact | `info@solevaeg.com` | `soleva front end/src/pages/PrivacyPage.tsx` |
| Terms & Conditions contact | `info@solevaeg.com` | `soleva front end/src/pages/TermsPage.tsx` |

### 🛒 **E-commerce & Support**
| Location | Email Used | File Path |
|----------|------------|-----------|
| Order confirmation emails | `sales@solevaeg.com` | Backend order processing |
| Support ticket replies | `support@solevaeg.com` | Backend support system |
| Account-related emails | `support@solevaeg.com` | Backend user management |

### 🔧 **Backend Configuration**
| Location | Email Used | File Path |
|----------|------------|-----------|
| Site Configuration (Admin) | All 4 emails configurable | `soleva back end/website_management/models.py` |
| Email templates | Dynamic based on context | `soleva back end/templates/emails/` |
| Django settings DEFAULT_FROM_EMAIL | `info@solevaeg.com` | `soleva back end/soleva_backend/settings.py` |

---

## 🎯 **Email Usage Guidelines**

### **info@solevaeg.com** - Primary Contact
- **Where**: Footer, Contact page, Privacy policy, Terms page
- **Purpose**: General inquiries, company information
- **Use cases**: 
  - "Contact us" forms
  - General website inquiries
  - Company information requests

### **support@solevaeg.com** - Customer Support
- **Where**: Support forms, help sections, customer service
- **Purpose**: Customer assistance, technical support
- **Use cases**: 
  - Order issues
  - Product questions
  - Account problems
  - Return/refund requests

### **sales@solevaeg.com** - Sales Team
- **Where**: Product inquiries, bulk order forms
- **Purpose**: Sales-related communications
- **Use cases**: 
  - Product availability
  - Bulk order requests
  - Pricing inquiries
  - Order confirmations

### **business@solevaeg.com** - Business Development
- **Where**: Partnership pages, B2B sections
- **Purpose**: Business partnerships and collaborations
- **Use cases**: 
  - Partnership requests
  - Wholesale inquiries
  - Business collaborations
  - Vendor applications

---

## 🔄 **Dynamic Email Management**

The website now uses a **dynamic configuration system** where emails can be updated from the admin panel without code changes:

### Admin Panel Control
- Navigate to: **Admin Panel → Website Management → Site Configuration**
- Update any email address instantly
- Changes reflect across the entire website automatically

### Frontend Integration
- All components use `useWebsite()` context hook
- Emails are fetched from `siteConfig` object
- Fallback to hardcoded emails if API fails

### Files Using Dynamic Emails
```typescript
// Example usage in components
const { siteConfig } = useWebsite();
const primaryEmail = siteConfig?.primary_email || 'info@solevaeg.com';
```

---

## 📋 **Implementation Status**

✅ **Completed**
- [x] Updated all frontend email references
- [x] Implemented dynamic email configuration
- [x] Created admin panel for email management
- [x] Updated footer with dynamic emails
- [x] Updated contact page with correct emails
- [x] Updated legal pages (Privacy, Terms)
- [x] Facebook link updated to official URL

⏳ **Pending**
- [ ] Backend email templates configuration
- [ ] SMTP settings with official email accounts
- [ ] Email verification for all accounts

---

## 🚀 **Next Steps for Developer**

1. **SMTP Configuration**: Configure email server settings with the official email accounts
2. **Email Templates**: Update all email templates to use appropriate sender addresses
3. **Testing**: Test all email functionality with the new addresses
4. **DNS Setup**: Ensure all email addresses are properly configured in DNS/hosting
5. **SSL Certificates**: Ensure secure email transmission

---

*This mapping ensures consistent email usage across the entire Soleva website and provides easy management through the admin panel.*
