export const BRAND = {
  name: "Soleva",
  slogan: "Made to Move",
  accent: "#d1b16a",
  country: "مصر",
  city: "القاهرة"
};

export const COUPONS = [
  {
    code: "SOLEVA10",
    discount: 10,
    freeShipping: false,
    desc: { ar: "خصم 10% على قيمة السلة", en: "10% off your cart" },
    maxDiscount: 300
  },
  {
    code: "SOLEVA10",
    discount: 10,
    freeShipping: false,
    desc: { ar: "خصم 10% على قيمة السلة (حد أقصى 300 ج.م)", en: "10% off your cart (max 300 EGP)" },
    maxDiscount: 300
  },
  {
    code: "soleva10",
    discount: 10,
    freeShipping: false,
    desc: { ar: "خصم 10% على قيمة السلة (حد أقصى 300 ج.م)", en: "10% off your cart (max 300 EGP)" },
    maxDiscount: 300
  },
  {
    code: "FREESHIP",
    discount: 0,
    freeShipping: true,
    desc: { ar: "شحن مجاني لأي طلب", en: "Free shipping on any order" },
    maxDiscount: null
  }
];