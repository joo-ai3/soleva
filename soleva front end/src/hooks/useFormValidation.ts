import { useState, useCallback } from 'react';
import { ShippingAddress } from '../types';

export interface ValidationErrors {
  [key: string]: string;
}

export interface FormValidationProps {
  name: string;
  primaryPhone: string;
  secondaryPhone?: string;
  shippingAddress: ShippingAddress | null;
  paymentMethod: string;
  senderNumber?: string;
  paymentScreenshot?: File | null;
}

export const useFormValidation = (lang: 'ar' | 'en') => {
  const [errors, setErrors] = useState<ValidationErrors>({});

  const getErrorMessage = (field: string, type: string): string => {
    const messages = {
      name: {
        required: lang === 'ar' ? 'الاسم مطلوب' : 'Name is required',
        minLength: lang === 'ar' ? 'الاسم يجب أن يحتوي على 3 حروف على الأقل' : 'Name must be at least 3 characters'
      },
      primaryPhone: {
        required: lang === 'ar' ? 'رقم الهاتف الأساسي مطلوب' : 'Primary phone is required',
        invalid: lang === 'ar' ? 'رقم الهاتف الأساسي غير صحيح' : 'Invalid primary phone number'
      },
      governorate: {
        required: lang === 'ar' ? 'يرجى اختيار المحافظة' : 'Please select governorate'
      },
      city: {
        required: lang === 'ar' ? 'يرجى اختيار المدينة/المركز' : 'Please select city/center'
      },
      detailedAddress: {
        required: lang === 'ar' ? 'العنوان التفصيلي مطلوب' : 'Detailed address is required',
        minLength: lang === 'ar' ? 'العنوان يجب أن يكون مفصلاً أكثر' : 'Address must be more detailed'
      },
      senderNumber: {
        required: lang === 'ar' ? 'يرجى إدخال رقم المرسل' : 'Please enter sender number'
      },
      paymentScreenshot: {
        required: lang === 'ar' ? 'يرجى رفع لقطة شاشة للدفع' : 'Please upload payment screenshot'
      }
    };

    return messages[field as keyof typeof messages]?.[type as keyof typeof messages[keyof typeof messages]] || 
           (lang === 'ar' ? 'حقل غير صحيح' : 'Invalid field');
  };

  const validateField = useCallback((field: string, value: any, formData: FormValidationProps): string => {
    switch (field) {
      case 'name':
        if (!value || !value.trim()) {
          return getErrorMessage('name', 'required');
        }
        if (value.trim().length < 3) {
          return getErrorMessage('name', 'minLength');
        }
        break;

      case 'primaryPhone':
        if (!value || !value.trim()) {
          return getErrorMessage('primaryPhone', 'required');
        }
        if (value.trim().length < 10) {
          return getErrorMessage('primaryPhone', 'invalid');
        }
        break;

      case 'governorate':
        if (!formData.shippingAddress?.governorate) {
          return getErrorMessage('governorate', 'required');
        }
        break;

      case 'city':
        if (!formData.shippingAddress?.city) {
          return getErrorMessage('city', 'required');
        }
        break;

      case 'detailedAddress':
        if (!formData.shippingAddress?.detailedAddress || !formData.shippingAddress.detailedAddress.trim()) {
          return getErrorMessage('detailedAddress', 'required');
        }
        if (formData.shippingAddress.detailedAddress.trim().length < 10) {
          return getErrorMessage('detailedAddress', 'minLength');
        }
        break;

      case 'senderNumber':
        if (formData.paymentMethod === 'digital' && (!value || !value.trim())) {
          return getErrorMessage('senderNumber', 'required');
        }
        break;

      case 'paymentScreenshot':
        if (formData.paymentMethod !== 'cash' && !value) {
          return getErrorMessage('paymentScreenshot', 'required');
        }
        break;

      default:
        return '';
    }
    return '';
  }, [lang]);

  const validateForm = useCallback((formData: FormValidationProps): ValidationErrors => {
    const newErrors: ValidationErrors = {};

    // Validate all fields
    const fieldsToValidate = [
      'name', 
      'primaryPhone', 
      'governorate', 
      'city', 
      'detailedAddress',
      'senderNumber',
      'paymentScreenshot'
    ];

    fieldsToValidate.forEach(field => {
      let value;
      switch (field) {
        case 'name':
          value = formData.name;
          break;
        case 'primaryPhone':
          value = formData.primaryPhone;
          break;
        case 'governorate':
        case 'city':
        case 'detailedAddress':
          value = formData.shippingAddress;
          break;
        case 'senderNumber':
          value = formData.senderNumber;
          break;
        case 'paymentScreenshot':
          value = formData.paymentScreenshot;
          break;
        default:
          value = '';
      }

      const error = validateField(field, value, formData);
      if (error) {
        newErrors[field] = error;
      }
    });

    setErrors(newErrors);
    return newErrors;
  }, [validateField]);

  const clearError = useCallback((field: string) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[field];
      return newErrors;
    });
  }, []);

  const clearAllErrors = useCallback(() => {
    setErrors({});
  }, []);

  return {
    errors,
    validateForm,
    validateField,
    clearError,
    clearAllErrors,
    hasErrors: Object.keys(errors).length > 0
  };
};
