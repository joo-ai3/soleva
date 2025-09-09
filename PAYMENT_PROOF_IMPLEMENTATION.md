# Payment Proof Upload Implementation

## Overview

This document outlines the implementation of payment proof upload functionality for Bank Wallet and E-Wallet payment methods in the Soleva e-commerce platform.

## Features Implemented

### Backend Features

1. **New PaymentProof Model** (`orders/models.py`)
   - Image upload with validation
   - Verification status tracking (pending, verified, rejected, needs_clarification)
   - File metadata (original filename, size, upload IP)
   - Admin verification workflow
   - Automatic file size calculation

2. **Updated Order Model** (`orders/models.py`)
   - Updated payment method choices:
     - `cash_on_delivery` - Cash on Delivery
     - `bank_wallet` - Bank Wallet Payment
     - `e_wallet` - E-Wallet Payment
     - `paymob` - Paymob
     - `stripe` - Stripe

3. **Payment Proof Serializers** (`orders/serializers.py`)
   - `PaymentProofSerializer` - For viewing payment proofs
   - `PaymentProofUploadSerializer` - For uploading with validation
   - `PaymentProofVerificationSerializer` - For admin verification

4. **API Endpoints** (`orders/views.py` & `orders/urls.py`)
   - `POST /orders/orders/{id}/upload-payment-proof/` - Upload payment proof
   - `GET /orders/payment-proofs/` - List payment proofs
   - `GET /orders/payment-proofs/{id}/` - Get payment proof details
   - `POST /orders/payment-proofs/{id}/verify_payment/` - Verify payment proof (admin only)

5. **Django Admin Integration** (`orders/admin.py`)
   - Payment proof inline in order admin
   - Dedicated payment proof admin with image preview
   - Verification status management
   - Automatic order status updates on verification

### Frontend Features

1. **Updated Payment Methods** (`CheckoutPage.tsx`)
   - Updated payment method IDs to match backend
   - `cash_on_delivery`, `bank_wallet`, `e_wallet`

2. **Payment Proof Upload Component** (`PaymentProofUpload.tsx`)
   - Drag & drop file upload
   - Image preview and validation
   - File size and type restrictions (max 10MB, JPEG/PNG/GIF/WebP)
   - Optional description field
   - Upload progress and error handling

3. **Payment Proof Viewer Component** (`PaymentProofViewer.tsx`)
   - Display uploaded payment proofs
   - Verification status indicators
   - Image modal for full-size viewing
   - Download functionality
   - Admin notes display

4. **Payment Proof Section Component** (`PaymentProofSection.tsx`)
   - Integrated section for order details pages
   - Conditional display based on payment method
   - Upload prompt for required payment methods
   - Status tracking and updates

5. **Updated API Services** (`api.ts`)
   - Payment proof upload endpoint
   - Payment proof management endpoints
   - Form data handling for file uploads

6. **Updated TypeScript Types** (`types/index.ts`)
   - `PaymentProof` interface
   - Updated `Order` interface with payment_proofs
   - Updated payment method types

## File Upload Specifications

### Validation Rules
- **File Types**: JPEG, PNG, GIF, WebP
- **Maximum Size**: 10MB
- **Required For**: Bank Wallet and E-Wallet payments only
- **Upload Location**: `payment_proofs/%Y/%m/` directory structure

### Security Features
- IP address logging for uploads
- User authentication required
- File type validation
- File size restrictions
- Secure file storage

## Verification Workflow

### Customer Flow
1. Customer selects Bank Wallet or E-Wallet payment method
2. Customer completes order
3. System prompts for payment proof upload
4. Customer uploads receipt/screenshot with optional description
5. System stores proof with "pending" status

### Admin Flow
1. Admin receives order with payment proof
2. Admin views proof in Django admin panel
3. Admin can:
   - **Verify** - Marks payment as verified, updates order status to "paid"
   - **Reject** - Marks proof as rejected, allows customer to re-upload
   - **Request Clarification** - Requests additional information
4. Customer receives notification of verification status
5. Order processing continues based on verification result

## Database Schema

### PaymentProof Model Fields
```python
- id (AutoField)
- order (ForeignKey to Order)
- image (ImageField)
- original_filename (CharField)
- file_size (PositiveIntegerField)
- uploaded_by (ForeignKey to User, nullable)
- upload_ip (GenericIPAddressField, nullable)
- verification_status (CharField with choices)
- verified_by (ForeignKey to User, nullable)
- verification_notes (TextField)
- verified_at (DateTimeField, nullable)
- description (TextField)
- created_at (DateTimeField)
- updated_at (DateTimeField)
```

### Indexes
- `order` - For efficient order lookups
- `verification_status` - For filtering by status
- `created_at` - For chronological ordering

## API Response Examples

### Upload Payment Proof
```json
POST /orders/orders/123/upload-payment-proof/
Content-Type: multipart/form-data

{
  "message": "Payment proof uploaded successfully.",
  "payment_proof": {
    "id": 1,
    "image": "/media/payment_proofs/2024/01/receipt.jpg",
    "original_filename": "receipt.jpg",
    "file_size": 2048576,
    "file_size_mb": 2.0,
    "verification_status": "pending",
    "description": "Payment made via mobile banking",
    "created_at": "2024-01-15T10:30:00Z",
    "is_verified": false
  }
}
```

### Order with Payment Proofs
```json
GET /orders/orders/123/

{
  "id": 123,
  "order_number": "ORD-2024-001",
  "payment_method": "bank_wallet",
  "payment_proofs": [
    {
      "id": 1,
      "image": "/media/payment_proofs/2024/01/receipt.jpg",
      "verification_status": "verified",
      "verified_at": "2024-01-15T12:00:00Z",
      "verified_by_name": "Admin User",
      "is_verified": true
    }
  ]
}
```

## Migration Requirements

After implementing these changes, run the following Django commands:

```bash
# Create migration for new PaymentProof model
python manage.py makemigrations orders --name add_payment_proof

# Apply the migration
python manage.py migrate

# Create superuser if needed for admin access
python manage.py createsuperuser
```

## Deployment Considerations

### Media Files
- Ensure media files directory is properly configured
- Set up appropriate file serving for production (Nginx, AWS S3, etc.)
- Configure proper permissions for uploaded files

### Security
- Implement rate limiting for file uploads
- Consider virus scanning for uploaded files
- Set up proper backup for payment proof files
- Ensure HTTPS is enabled for secure file uploads

### Storage
- Monitor disk usage for uploaded files
- Implement file cleanup policies if needed
- Consider cloud storage for scalability

## Testing

### Backend Tests
- Model validation tests
- API endpoint tests
- File upload validation tests
- Admin integration tests

### Frontend Tests
- Component rendering tests
- File upload functionality tests
- Error handling tests
- User interaction tests

## Future Enhancements

1. **Automatic OCR** - Extract payment details from uploaded images
2. **Payment Matching** - Automatically match payments with bank transaction APIs
3. **Bulk Verification** - Allow admins to verify multiple proofs at once
4. **Mobile App Integration** - Camera capture for payment proofs
5. **Email Notifications** - Automated status update emails
6. **Analytics Dashboard** - Payment proof statistics and trends

## Support

For any issues or questions regarding the payment proof implementation, please refer to:
- Django documentation for model and admin customization
- DRF documentation for API development
- React documentation for component development
- The project's main README.md for general setup instructions
