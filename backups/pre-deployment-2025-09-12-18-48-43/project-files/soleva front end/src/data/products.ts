export const collections = [
  {
    id: "mens",
    name: { ar: "أحذية رجالي", en: "Men's Shoes" },
    desc: { ar: "تشكيلة أنيقة للرجال", en: "Elegant collection for men" },
    image: "https://images.pexels.com/photos/1598508/pexels-photo-1598508.jpeg?auto=compress&cs=tinysrgb&w=600"
  },
  {
    id: "womens",
    name: { ar: "أحذية نسائي", en: "Women's Shoes" },
    desc: { ar: "تشكيلة عصرية للنساء", en: "Modern collection for women" },
    image: "https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg?auto=compress&cs=tinysrgb&w=600"
  },
  {
    id: "basics",
    name: { ar: "سوليفا أساسي", en: "Soleva Essentials" },
    desc: { ar: "خط اقتصادي عملي", en: "Budget-friendly essentials" },
    image: "https://images.pexels.com/photos/1464625/pexels-photo-1464625.jpeg?auto=compress&cs=tinysrgb&w=600"
  },
];

export const products = [
  // Men's Shoes
  {
    id: 1,
    name: { ar: "Soleva Classic Men", en: "Soleva Classic Men" },
    price: 3900,
    image: "https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg?auto=compress&cs=tinysrgb&w=600",
    desc: {
      ar: "حذاء رجالي كلاسيكي بتصميم أنيق وخامات فاخرة.",
      en: "Classic men's shoe with elegant design and premium materials."
    },
    specs: {
      ar: [["الخامة", "جلد طبيعي"], ["النعل", "مطاط فاخر"], ["اللون", "أسود/بني"]],
      en: [["Material", "Genuine Leather"], ["Sole", "Premium Rubber"], ["Color", "Black/Brown"]]
    },
    collection: "mens",
    colors: [
      { name: { ar: "أسود", en: "Black" }, code: "#191919" },
      { name: { ar: "بني", en: "Brown" }, code: "#8B4513" }
    ],
    sizes: [40, 41, 42, 43, 44, 45]
  },
  {
    id: 2,
    name: { ar: "Soleva Sport Men", en: "Soleva Sport Men" },
    price: 2800,
    image: "https://images.pexels.com/photos/1464625/pexels-photo-1464625.jpeg?auto=compress&cs=tinysrgb&w=600",
    desc: {
      ar: "حذاء رياضي للرجال مريح وعملي للاستخدام اليومي.",
      en: "Comfortable men's athletic shoe for daily wear."
    },
    specs: {
      ar: [["الخامة", "شبك مقاوم"], ["النعل", "مطاط مرن"], ["اللون", "أبيض/رمادي"]],
      en: [["Material", "Resistant Mesh"], ["Sole", "Flexible Rubber"], ["Color", "White/Gray"]]
    },
    collection: "mens",
    colors: [
      { name: { ar: "أبيض", en: "White" }, code: "#f9f9f9" },
      { name: { ar: "رمادي", en: "Gray" }, code: "#808080" }
    ],
    sizes: [39, 40, 41, 42, 43, 44]
  },
  // Women's Shoes
  {
    id: 3,
    name: { ar: "Soleva Elegance Women", en: "Soleva Elegance Women" },
    price: 3500,
    image: "https://images.pexels.com/photos/1598508/pexels-photo-1598508.jpeg?auto=compress&cs=tinysrgb&w=600",
    desc: {
      ar: "حذاء نسائي أنيق مثالي للمناسبات الخاصة.",
      en: "Elegant women's shoe perfect for special occasions."
    },
    specs: {
      ar: [["الخامة", "جلد ناعم"], ["الكعب", "متوسط"], ["اللون", "أحمر/أسود"]],
      en: [["Material", "Soft Leather"], ["Heel", "Medium"], ["Color", "Red/Black"]]
    },
    collection: "womens",
    colors: [
      { name: { ar: "أحمر", en: "Red" }, code: "#DC143C" },
      { name: { ar: "أسود", en: "Black" }, code: "#191919" }
    ],
    sizes: [36, 37, 38, 39, 40, 41]
  },
  {
    id: 4,
    name: { ar: "Soleva Comfort Women", en: "Soleva Comfort Women" },
    price: 2400,
    image: "https://images.pexels.com/photos/2529148/pexels-photo-2529148.jpeg?auto=compress&cs=tinysrgb&w=600",
    desc: {
      ar: "حذاء نسائي مريح للاستخدام اليومي.",
      en: "Comfortable women's shoe for everyday use."
    },
    specs: {
      ar: [["الخامة", "قماش مرن"], ["النعل", "مبطن"], ["اللون", "بيج/وردي"]],
      en: [["Material", "Flexible Fabric"], ["Sole", "Cushioned"], ["Color", "Beige/Pink"]]
    },
    collection: "womens",
    colors: [
      { name: { ar: "بيج", en: "Beige" }, code: "#F5F5DC" },
      { name: { ar: "وردي", en: "Pink" }, code: "#FFC0CB" }
    ],
    sizes: [36, 37, 38, 39, 40]
  },
  // Soleva Basics
  {
    id: 5,
    name: { ar: "Soleva Essential Classic", en: "Soleva Essential Classic" },
    price: 1800,
    image: "https://images.pexels.com/photos/1464625/pexels-photo-1464625.jpeg?auto=compress&cs=tinysrgb&w=600",
    desc: {
      ar: "حذاء أساسي بسعر اقتصادي وجودة ممتازة.",
      en: "Essential shoe with budget-friendly price and excellent quality."
    },
    specs: {
      ar: [["الخامة", "جلد صناعي"], ["النعل", "مطاط"], ["اللون", "أسود/أبيض"]],
      en: [["Material", "Synthetic Leather"], ["Sole", "Rubber"], ["Color", "Black/White"]]
    },
    collection: "basics",
    colors: [
      { name: { ar: "أسود", en: "Black" }, code: "#191919" },
      { name: { ar: "أبيض", en: "White" }, code: "#f9f9f9" }
    ],
    sizes: [38, 39, 40, 41, 42, 43]
  },
  {
    id: 6,
    name: { ar: "Soleva Essential Sport", en: "Soleva Essential Sport" },
    price: 1500,
    image: "https://images.pexels.com/photos/1598508/pexels-photo-1598508.jpeg?auto=compress&cs=tinysrgb&w=600",
    desc: {
      ar: "حذاء رياضي أساسي مريح وعملي.",
      en: "Basic athletic shoe that's comfortable and practical."
    },
    specs: {
      ar: [["الخامة", "قماش"], ["النعل", "مطاط خفيف"], ["اللون", "رمادي/أزرق"]],
      en: [["Material", "Canvas"], ["Sole", "Light Rubber"], ["Color", "Gray/Blue"]]
    },
    collection: "basics",
    colors: [
      { name: { ar: "رمادي", en: "Gray" }, code: "#808080" },
      { name: { ar: "أزرق", en: "Blue" }, code: "#4169E1" }
    ],
    sizes: [37, 38, 39, 40, 41, 42]
  }
];