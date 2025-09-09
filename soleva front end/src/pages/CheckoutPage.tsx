import React, { useState, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiCreditCard, FiUser, FiPhone, FiDollarSign, FiSmartphone, FiZap, FiUpload } from 'react-icons/fi';
import { useCart } from '../contexts/CartContext';
import { useLang, useTranslation } from '../contexts/LangContext';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';
import AddressSelector from '../components/AddressSelector';
import ErrorMessage from '../components/ErrorMessage';
import { useFormValidation } from '../hooks/useFormValidation';
import { ShippingAddress } from '../types';

export default function CheckoutPage() {
  const { cart, clearCart } = useCart();
  const { lang } = useLang();
  const t = useTranslation();
  const navigate = useNavigate();
  const location = useLocation();
  const applied = location.state?.appliedCoupon || null;

  const [formData, setFormData] = useState({
    name: "",
    primaryPhone: "",
    secondaryPhone: "",
    paymentMethod: "cash_on_delivery",
    senderNumber: "",
    paymentScreenshot: null as File | null
  });

  const [shippingAddress, setShippingAddress] = useState<ShippingAddress | null>(null);

  const [error, setError] = useState("");
  const [isUploading] = useState(false);

  // Form validation
  const { errors, validateForm, clearError } = useFormValidation(lang as 'ar' | 'en');
  
  // Refs for auto-scrolling to error fields
  const fieldRefs = {
    name: useRef<HTMLInputElement>(null),
    primaryPhone: useRef<HTMLInputElement>(null),
    address: useRef<HTMLDivElement>(null),
    senderNumber: useRef<HTMLInputElement>(null),
    paymentScreenshot: useRef<HTMLInputElement>(null)
  };

  const subtotal = cart.reduce((acc, item) => acc + item.unit_price * item.quantity, 0);
  const discount = applied?.discount ? Math.min(Math.floor((subtotal * applied.discount) / 100), applied.maxDiscount || Infinity) : 0;
  const shipping = applied?.freeShipping ? 0 : (shippingAddress?.shippingCost || 0);
  const total = subtotal - discount + (cart.length > 0 && shippingAddress?.shippingCost ? shipping : 0);

  const paymentMethods = [
    {
      id: "cash_on_delivery",
      name: t("cashOnDelivery"),
      icon: <FiDollarSign />,
      desc: lang === "ar" ? "ادفع عند استلام الطلب" : "Pay when you receive your order"
    },
    {
      id: "bank_wallet",
      name: t("bankWallet"),
      icon: <FiCreditCard />,
      desc: lang === "ar" ? "الدفع عبر محفظة البنك" : "Pay through bank wallet"
    },
    {
      id: "e_wallet",
      name: t("digitalWallet"),
      icon: <FiZap />,
      desc: lang === "ar" ? "الدفع عبر المحفظة الرقمية" : "Pay through digital wallet"
    }
  ];

  const scrollToError = (fieldName: string) => {
    const ref = fieldRefs[fieldName as keyof typeof fieldRefs];
    if (ref?.current) {
      ref.current.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center'
      });
      
      // Focus the field if it's an input
      if (ref.current instanceof HTMLInputElement) {
        setTimeout(() => ref.current?.focus(), 300);
      }
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    // Validate form using the validation hook
    const validationData = {
      name: formData.name,
      primaryPhone: formData.primaryPhone,
      secondaryPhone: formData.secondaryPhone,
      shippingAddress,
      paymentMethod: formData.paymentMethod,
      senderNumber: formData.senderNumber,
      paymentScreenshot: formData.paymentScreenshot
    };

    const validationErrors = validateForm(validationData);

    if (Object.keys(validationErrors).length > 0) {
      // Scroll to first error field
      const firstErrorField = Object.keys(validationErrors)[0];
      scrollToError(firstErrorField);
      return;
    }

    setError("");
    
    if (formData.paymentMethod !== "cash") {
      // Show payment under review message
      alert(lang === "ar" 
        ? "دفعتك قيد المراجعة. سيتم إشعارك قريباً." 
        : "Your payment is under review. You will be notified shortly."
      );
    }
    
    clearCart();
    setFormData({ 
      name: "", 
      primaryPhone: "", 
      secondaryPhone: "", 
      paymentMethod: "cash",
      senderNumber: "",
      paymentScreenshot: null
    });
    setShippingAddress(null);
    navigate("/order-confirmation", { state: { ...formData, shippingAddress, total } });
  };

  if (cart.length === 0) {
    return (
      <div className="container mx-auto py-20 text-center">
        <p className="text-xl">{t("empty")}</p>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.7 }}
      className="container mx-auto py-6 sm:py-10 px-4 max-w-4xl"
    >
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
        {/* Checkout Form */}
        <div className="lg:col-span-2">
          <GlassCard>
            <h1 className="text-2xl sm:text-3xl font-bold mb-6 sm:mb-8 text-center font-montserrat">{t("checkout")}</h1>

            <form onSubmit={handleSubmit} className="space-y-6">
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-red-100 border border-red-300 text-red-700 p-3 rounded-lg text-sm"
                >
                  {error}
                </motion.div>
              )}

              {/* Full Name */}
              <div>
                <label className={`block text-sm font-semibold mb-2 ${errors.name ? 'text-red-600' : 'text-gray-700'}`}>
                  <FiUser className="inline mr-2" />
                  {t("fullName")}
                  <span className="text-red-500 mr-1">*</span>
                </label>
                <input
                  ref={fieldRefs.name}
                  required
                  className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 min-w-0 transition-colors ${
                    errors.name 
                      ? 'border-red-500 focus:ring-red-500 bg-red-50/50' 
                      : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
                  }`}
                  value={formData.name}
                  onChange={e => {
                    setFormData({ ...formData, name: e.target.value });
                    if (errors.name) clearError('name');
                  }}
                  placeholder={lang === "ar" ? "أدخل اسمك الكامل" : "Enter your full name"}
                />
                <ErrorMessage error={errors.name} />
              </div>

              {/* Phone Numbers */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className={`block text-sm font-semibold mb-2 ${errors.primaryPhone ? 'text-red-600' : 'text-gray-700'}`}>
                    <FiPhone className="inline mr-2" />
                    {t("primaryPhone")}
                    <span className="text-red-500 mr-1">*</span>
                  </label>
                  <input
                    ref={fieldRefs.primaryPhone}
                    required
                    type="tel"
                    className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 min-w-0 transition-colors ${
                      errors.primaryPhone 
                        ? 'border-red-500 focus:ring-red-500 bg-red-50/50' 
                        : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
                    }`}
                    value={formData.primaryPhone}
                    onChange={e => {
                      setFormData({ ...formData, primaryPhone: e.target.value });
                      if (errors.primaryPhone) clearError('primaryPhone');
                    }}
                    placeholder={lang === "ar" ? "رقم الهاتف الأساسي" : "Primary phone number"}
                  />
                  <ErrorMessage error={errors.primaryPhone} />
                </div>
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    <FiSmartphone className="inline mr-2" />
                    {t("secondaryPhone")}
                  </label>
                  <input
                    type="tel"
                    className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] min-w-0"
                    value={formData.secondaryPhone}
                    onChange={e => setFormData({ ...formData, secondaryPhone: e.target.value })}
                    placeholder={lang === "ar" ? "رقم هاتف إضافي" : "Secondary phone number"}
                  />
                </div>
              </div>

              {/* Address Selector */}
              <div ref={fieldRefs.address}>
                <AddressSelector
                  onAddressChange={(address) => {
                    setShippingAddress(address);
                    // Clear address-related errors when address changes
                    if (address?.governorate && errors.governorate) clearError('governorate');
                    if (address?.city && errors.city) clearError('city');
                    if (address?.detailedAddress && errors.detailedAddress) clearError('detailedAddress');
                  }}
                  selectedGovernorate={shippingAddress?.governorate}
                  selectedCity={shippingAddress?.city}
                  detailedAddress={shippingAddress?.detailedAddress}
                  errors={{
                    governorate: errors.governorate,
                    city: errors.city,
                    detailedAddress: errors.detailedAddress
                  }}
                />
              </div>

              {/* Payment Method */}
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-4">
                  <FiCreditCard className="inline mr-2" />
                  {t("paymentMethod")}
                </label>
                <div className="payment-methods-grid grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {paymentMethods.map((method) => (
                    <motion.div
                      key={method.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`payment-method-card glass p-4 rounded-xl border-2 cursor-pointer transition-all ${
                        formData.paymentMethod === method.id
                          ? 'selected border-[#d1b16a] bg-[#d1b16a]/10'
                          : 'border-gray-200 hover:border-[#d1b16a]/50'
                      }`}
                      onClick={() => setFormData({ ...formData, paymentMethod: method.id })}
                    >
                      <div className="flex flex-col items-center text-center">
                        <div className={`text-2xl mb-2 ${formData.paymentMethod === method.id ? 'text-[#d1b16a]' : 'text-gray-400'}`}>
                          {method.icon}
                        </div>
                        <div className="font-semibold text-sm mb-1">{method.name}</div>
                        <div className="text-xs text-gray-500">{method.desc}</div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Payment Details for E-wallet and Bank */}
              {formData.paymentMethod !== "cash_on_delivery" && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.3 }}
                  className="space-y-4"
                >
                  {/* Payment Information Display */}
                  <div>
                    <div className="glass p-4 rounded-xl bg-[#d1b16a]/10 border border-[#d1b16a]/30">
                      <h4 className="font-semibold text-gray-700 mb-2">
                        {formData.paymentMethod === "e_wallet" 
                          ? (lang === "ar" ? "معلومات المحفظة الرقمية" : "Digital Wallet Information")
                          : (lang === "ar" ? "معلومات التحويل البنكي" : "Bank Transfer Information")
                        }
                      </h4>
                      <div className="text-lg font-bold text-[#d1b16a] mb-2">
                        {formData.paymentMethod === "e_wallet" 
                          ? (lang === "ar" ? "رقم المحفظة: " : "Wallet Number: ") + "01028354015"
                          : (lang === "ar" ? "رقم الحساب: " : "Account Number: ") + "1234567890123456"
                        }
                      </div>
                      <p className="text-sm text-gray-600">
                        {lang === "ar" 
                          ? "يرجى إرسال المبلغ إلى الرقم أعلاه ثم رفع لقطة شاشة للتأكيد"
                          : "Please send the amount to the number above and upload a screenshot for confirmation"
                        }
                      </p>
                    </div>
                  </div>

                  {/* Sender Number - Only for Digital Wallet */}
                  {formData.paymentMethod === "e_wallet" && (
                    <div>
                      <label className={`block text-sm font-semibold mb-2 ${errors.senderNumber ? 'text-red-600' : 'text-gray-700'}`}>
                        {lang === "ar" ? "رقم المرسل المستخدم للتحويل" : "Sender Number Used for Transfer"}
                        <span className="text-red-500 mr-1">*</span>
                      </label>
                      <input
                        ref={fieldRefs.senderNumber}
                        required
                        type="tel"
                        className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 min-w-0 transition-colors ${
                          errors.senderNumber 
                            ? 'border-red-500 focus:ring-red-500 bg-red-50/50' 
                            : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
                        }`}
                        value={formData.senderNumber}
                        onChange={e => {
                          setFormData({ ...formData, senderNumber: e.target.value });
                          if (errors.senderNumber) clearError('senderNumber');
                        }}
                        placeholder={lang === "ar" ? "رقم الهاتف المستخدم للدفع" : "Phone number used for payment"}
                      />
                      <ErrorMessage error={errors.senderNumber} />
                    </div>
                  )}

                  {/* Screenshot Upload */}
                  <div>
                    <label className={`block text-sm font-semibold mb-2 ${errors.paymentScreenshot ? 'text-red-600' : 'text-gray-700'}`}>
                      <FiUpload className="inline mr-2" />
                      {lang === "ar" ? "لقطة شاشة للدفع" : "Payment Screenshot"}
                      <span className="text-red-500 mr-1">*</span>
                    </label>
                    <input
                      ref={fieldRefs.paymentScreenshot}
                      required
                      type="file"
                      accept="image/*"
                      className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 min-w-0 transition-colors ${
                        errors.paymentScreenshot 
                          ? 'border-red-500 focus:ring-red-500 bg-red-50/50' 
                          : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
                      }`}
                      onChange={e => {
                        const file = e.target.files?.[0] || null;
                        setFormData({ ...formData, paymentScreenshot: file });
                        if (errors.paymentScreenshot) clearError('paymentScreenshot');
                      }}
                    />
                    <ErrorMessage error={errors.paymentScreenshot} />
                    <p className="text-xs text-gray-500 mt-1">
                      {lang === "ar" 
                        ? "يرجى رفع لقطة شاشة تؤكد عملية الدفع" 
                        : "Please upload a screenshot confirming the payment"
                      }
                    </p>
                  </div>
                </motion.div>
              )}

              {/* Submit */}
              <GlassButton
                type="submit"
                className="w-full bg-[#d1b16a] text-black border-none hover:bg-[#d1b16a]/80 text-lg sm:text-xl py-4 min-h-[56px] font-bold hover:scale-105 transition-all duration-300"
                disabled={isUploading}
              >
                {isUploading ? (
                  <div className="w-6 h-6 border-2 border-black/20 border-t-black rounded-full animate-spin" />
                ) : (
                  <>
                    <FiCreditCard size={24} />
                    {t("placeOrder")}
                  </>
                )}
              </GlassButton>
            </form>
          </GlassCard>
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <GlassCard className="sticky top-24">
            <h3 className="text-xl font-bold mb-6">{t("total")}</h3>

            {/* Cart Items */}
            <div className="space-y-3 mb-6">
              {cart.map((item, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="flex items-center gap-3 p-3 glass rounded-lg"
                >
                  <img
                    src={item.product_image || '/placeholder.jpg'}
                    alt={item.product_name}
                    className="w-12 h-12 object-cover rounded-lg"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="font-medium text-sm line-clamp-1">{item.product_name}</div>
                    <div className="text-xs text-gray-500">
                      {item.variant_attributes?.color} • {item.variant_attributes?.size} • x{item.quantity}
                    </div>
                  </div>
                  <div className="text-sm font-bold text-[#d1b16a]">
                    {item.unit_price * item.quantity} {t("egp")}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Summary */}
            <div className="glass p-4 rounded-xl bg-gray-50/50">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>{lang === "ar" ? "الإجمالي قبل الخصم" : "Subtotal"}:</span>
                  <span>{subtotal} {t("egp")}</span>
                </div>
                {discount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>{t("couponDiscount")} ({applied.code.toUpperCase()}):</span>
                    <span>-{discount} {t("egp")}</span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span>
                    {t("shipping")}
                    {shippingAddress && (
                      <span className="text-xs text-gray-500 block">
                        ({t("shippingCostTo")} {shippingAddress.governorateName[lang as keyof typeof shippingAddress.governorateName]})
                      </span>
                    )}:
                  </span>
                  <span>
                    {!shippingAddress?.governorate ? (
                      <span className="text-sm text-gray-500">
                        {lang === "ar" ? "يرجى اختيار المحافظة لحساب تكلفة الشحن" : "Please select your governorate to calculate shipping"}
                      </span>
                    ) : shipping === 0 ? t("free") : `${shipping} ${t("egp")}`}
                  </span>
                </div>
                <div className="flex justify-between font-bold text-lg pt-2 border-t">
                  <span>{t("total")}:</span>
                  <span className="text-[#d1b16a]">
                    {!shippingAddress?.governorate ? (
                      <>
                        {subtotal - discount} {t("egp")} + {lang === "ar" ? "الشحن" : "Shipping"}
                      </>
                    ) : (
                      `${total} ${t("egp")}`
                    )}
                  </span>
                </div>
              </div>
            </div>
          </GlassCard>
        </div>
      </div>
    </motion.div>
  );
}