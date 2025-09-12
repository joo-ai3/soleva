export interface City {
  id: string;
  name: {
    ar: string;
    en: string;
  };
}

export interface Governorate {
  id: string;
  name: {
    ar: string;
    en: string;
  };
  shippingCost: number;
  cities: City[];
}

export const egyptData: Governorate[] = [
  {
    id: "cairo",
    name: { ar: "القاهرة", en: "Cairo" },
    shippingCost: 40,
    cities: [
      { id: "nasr-city", name: { ar: "مدينة نصر", en: "Nasr City" } },
      { id: "heliopolis", name: { ar: "مصر الجديدة", en: "Heliopolis" } },
      { id: "maadi", name: { ar: "المعادي", en: "Maadi" } },
      { id: "zamalek", name: { ar: "الزمالك", en: "Zamalek" } },
      { id: "downtown", name: { ar: "وسط البلد", en: "Downtown" } },
      { id: "shubra", name: { ar: "شبرا", en: "Shubra" } },
      { id: "helwan", name: { ar: "حلوان", en: "Helwan" } },
      { id: "new-cairo", name: { ar: "القاهرة الجديدة", en: "New Cairo" } },
      { id: "mokattam", name: { ar: "المقطم", en: "Mokattam" } },
      { id: "ain-shams", name: { ar: "عين شمس", en: "Ain Shams" } },
      { id: "hadayek-el-kobba", name: { ar: "حدائق القبة", en: "Hadayek El Kobba" } },
      { id: "rod-el-farag", name: { ar: "روض الفرج", en: "Rod El Farag" } },
      { id: "shoubra-el-kheima", name: { ar: "شبرا الخيمة", en: "Shoubra El Kheima" } },
      { id: "el-sahel", name: { ar: "الساحل", en: "El Sahel" } },
      { id: "abdeen", name: { ar: "عابدين", en: "Abdeen" } },
      { id: "azbakeya", name: { ar: "الأزبكية", en: "Azbakeya" } },
      { id: "bab-el-shaaria", name: { ar: "باب الشعرية", en: "Bab El Shaaria" } },
      { id: "bulaq", name: { ar: "بولاق", en: "Bulaq" } },
      { id: "darb-el-ahmar", name: { ar: "درب الأحمر", en: "Darb El Ahmar" } },
      { id: "el-gamaleya", name: { ar: "الجمالية", en: "El Gamaleya" } },
      { id: "el-khalifa", name: { ar: "الخليفة", en: "El Khalifa" } },
      { id: "el-mosky", name: { ar: "الموسكي", en: "El Mosky" } },
      { id: "el-sayeda-zeinab", name: { ar: "السيدة زينب", en: "El Sayeda Zeinab" } },
      { id: "el-zaher", name: { ar: "الظاهر", en: "El Zaher" } },
      { id: "manshiet-naser", name: { ar: "منشية ناصر", en: "Manshiet Naser" } },
      { id: "misr-el-qadima", name: { ar: "مصر القديمة", en: "Misr El Qadima" } },
      { id: "el-salam", name: { ar: "السلام", en: "El Salam" } },
      { id: "el-matareya", name: { ar: "المطرية", en: "El Matareya" } },
      { id: "el-marg", name: { ar: "المرج", en: "El Marg" } },
      { id: "el-nozha", name: { ar: "النزهة", en: "El Nozha" } },
      { id: "el-sharabiya", name: { ar: "الشرابية", en: "El Sharabiya" } },
      { id: "el-zawya-el-hamra", name: { ar: "الزاوية الحمراء", en: "El Zawya El Hamra" } },
      { id: "hadayek-el-qobba", name: { ar: "حدائق القبة", en: "Hadayek El Qobba" } },
      { id: "el-wayli", name: { ar: "الوايلي", en: "El Wayli" } },
      { id: "el-zeitoun", name: { ar: "الزيتون", en: "El Zeitoun" } },
      { id: "15th-may-city", name: { ar: "مدينة 15 مايو", en: "15th May City" } },
      { id: "el-basatin", name: { ar: "البساتين", en: "El Basatin" } },
      { id: "dar-el-salam", name: { ar: "دار السلام", en: "Dar El Salam" } },
      { id: "el-khalifa-district", name: { ar: "حي الخليفة", en: "El Khalifa District" } },
      { id: "el-maasara", name: { ar: "المعصرة", en: "El Maasara" } },
      { id: "el-tabbin", name: { ar: "التبين", en: "El Tabbin" } },
      { id: "tura", name: { ar: "طرة", en: "Tura" } },
      { id: "el-maadi-el-saghira", name: { ar: "المعادي الصغيرة", en: "El Maadi El Saghira" } }
    ]
  },
  {
    id: "giza",
    name: { ar: "الجيزة", en: "Giza" },
    shippingCost: 45,
    cities: [
      { id: "giza-city", name: { ar: "الجيزة", en: "Giza City" } },
      { id: "6th-october", name: { ar: "6 أكتوبر", en: "6th of October City" } },
      { id: "sheikh-zayed", name: { ar: "الشيخ زايد", en: "Sheikh Zayed City" } },
      { id: "haram", name: { ar: "الهرم", en: "Haram" } },
      { id: "faisal", name: { ar: "فيصل", en: "Faisal" } },
      { id: "dokki", name: { ar: "الدقي", en: "Dokki" } },
      { id: "mohandessin", name: { ar: "المهندسين", en: "Mohandessin" } },
      { id: "agouza", name: { ar: "العجوزة", en: "Agouza" } },
      { id: "imbaba", name: { ar: "إمبابة", en: "Imbaba" } },
      { id: "bulaq-el-dakrour", name: { ar: "بولاق الدكرور", en: "Bulaq El Dakrour" } },
      { id: "kerdasa", name: { ar: "كرداسة", en: "Kerdasa" } },
      { id: "abu-rawash", name: { ar: "أبو رواش", en: "Abu Rawash" } },
      { id: "badrasheen", name: { ar: "البدرشين", en: "Badrasheen" } },
      { id: "saqqara", name: { ar: "سقارة", en: "Saqqara" } },
      { id: "atfih", name: { ar: "أطفيح", en: "Atfih" } },
      { id: "el-hawamdeya", name: { ar: "الحوامدية", en: "El Hawamdeya" } },
      { id: "el-ayat", name: { ar: "العياط", en: "El Ayat" } },
      { id: "el-saff", name: { ar: "الصف", en: "El Saff" } },
      { id: "mansouriya", name: { ar: "المنصورية", en: "Mansouriya" } },
      { id: "el-tebbin", name: { ar: "التبين", en: "El Tebbin" } },
      { id: "el-munib", name: { ar: "المنيب", en: "El Munib" } },
      { id: "el-omraniya", name: { ar: "العمرانية", en: "El Omraniya" } },
      { id: "el-warraq", name: { ar: "الوراق", en: "El Warraq" } },
      { id: "kit-kat", name: { ar: "كيت كات", en: "Kit Kat" } },
      { id: "el-moneeb", name: { ar: "المنيب", en: "El Moneeb" } },
      { id: "hadayek-el-ahram", name: { ar: "حدائق الأهرام", en: "Hadayek El Ahram" } },
      { id: "abu-sir", name: { ar: "أبو صير", en: "Abu Sir" } },
      { id: "el-bahariya", name: { ar: "البحارية", en: "El Bahariya" } },
      { id: "dahshur", name: { ar: "دهشور", en: "Dahshur" } },
      { id: "el-lisht", name: { ar: "اللشت", en: "El Lisht" } },
      { id: "mazghuna", name: { ar: "مزغونة", en: "Mazghuna" } },
      { id: "meidum", name: { ar: "ميدوم", en: "Meidum" } },
      { id: "el-riqqa", name: { ar: "الريقة", en: "El Riqqa" } }
    ]
  },
  {
    id: "alexandria",
    name: { ar: "الإسكندرية", en: "Alexandria" },
    shippingCost: 60,
    cities: [
      { id: "montaza", name: { ar: "المنتزه", en: "Montaza" } },
      { id: "east-alex", name: { ar: "شرق الإسكندرية", en: "East Alexandria" } },
      { id: "middle-alex", name: { ar: "وسط الإسكندرية", en: "Middle Alexandria" } },
      { id: "west-alex", name: { ar: "غرب الإسكندرية", en: "West Alexandria" } },
      { id: "gomrok", name: { ar: "الجمرك", en: "Gomrok" } },
      { id: "attarin", name: { ar: "العطارين", en: "Attarin" } },
      { id: "labban", name: { ar: "اللبان", en: "Labban" } },
      { id: "mansheya", name: { ar: "المنشية", en: "Mansheya" } },
      { id: "amreya", name: { ar: "العامرية", en: "Amreya" } },
      { id: "borg-el-arab", name: { ar: "برج العرب", en: "Borg El Arab" } },
      { id: "king-mariout", name: { ar: "الملك مريوط", en: "King Mariout" } },
      { id: "new-borg-el-arab", name: { ar: "برج العرب الجديدة", en: "New Borg El Arab" } },
      { id: "el-raml", name: { ar: "الرمل", en: "El Raml" } },
      { id: "sidi-gaber", name: { ar: "سيدي جابر", en: "Sidi Gaber" } },
      { id: "sporting", name: { ar: "سبورتنج", en: "Sporting" } },
      { id: "stanley", name: { ar: "ستانلي", en: "Stanley" } },
      { id: "glim", name: { ar: "جليم", en: "Glim" } },
      { id: "siouf", name: { ar: "سيوف", en: "Siouf" } },
      { id: "fleming", name: { ar: "فلمنج", en: "Fleming" } },
      { id: "victoria", name: { ar: "فيكتوريا", en: "Victoria" } },
      { id: "camp-caesar", name: { ar: "كامب شيزار", en: "Camp Caesar" } },
      { id: "abu-qir", name: { ar: "أبو قير", en: "Abu Qir" } },
      { id: "el-maamoura", name: { ar: "المعمورة", en: "El Maamoura" } },
      { id: "el-mandara", name: { ar: "المندرة", en: "El Mandara" } },
      { id: "el-asafra", name: { ar: "العصافرة", en: "El Asafra" } },
      { id: "miami", name: { ar: "ميامي", en: "Miami" } },
      { id: "sidi-bishr", name: { ar: "سيدي بشر", en: "Sidi Bishr" } },
      { id: "el-ibrahimiya", name: { ar: "الإبراهيمية", en: "El Ibrahimiya" } },
      { id: "karmouz", name: { ar: "كرموز", en: "Karmouz" } },
      { id: "mina-el-basal", name: { ar: "مينا البصل", en: "Mina El Basal" } },
      { id: "el-wardian", name: { ar: "الورديان", en: "El Wardian" } },
      { id: "el-dekheila", name: { ar: "الدخيلة", en: "El Dekheila" } },
      { id: "el-agamy", name: { ar: "العجمي", en: "El Agamy" } },
      { id: "hannoville", name: { ar: "هانوفيل", en: "Hannoville" } },
      { id: "el-bitash", name: { ar: "البيطاش", en: "El Bitash" } }
    ]
  },
  {
    id: "dakahlia",
    name: { ar: "الدقهلية", en: "Dakahlia" },
    shippingCost: 65,
    cities: [
      { id: "mansoura", name: { ar: "المنصورة", en: "Mansoura" } },
      { id: "talkha", name: { ar: "طلخا", en: "Talkha" } },
      { id: "mit-ghamr", name: { ar: "ميت غمر", en: "Mit Ghamr" } },
      { id: "dekernes", name: { ar: "دكرنس", en: "Dekernes" } },
      { id: "aga", name: { ar: "أجا", en: "Aga" } },
      { id: "manzala", name: { ar: "المنزلة", en: "Manzala" } },
      { id: "temay-el-amdid", name: { ar: "تمي الأمديد", en: "Temay El Amdid" } },
      { id: "sherbin", name: { ar: "شربين", en: "Sherbin" } },
      { id: "matareya", name: { ar: "المطرية", en: "Matareya" } },
      { id: "belqas", name: { ar: "بلقاس", en: "Belqas" } },
      { id: "meet-salsil", name: { ar: "ميت سلسيل", en: "Meet Salsil" } },
      { id: "gamasa", name: { ar: "جمصة", en: "Gamasa" } },
      { id: "nabaroh", name: { ar: "نبروه", en: "Nabaroh" } },
      { id: "sinbellawein", name: { ar: "سنبلاوين", en: "Sinbellawein" } },
      { id: "dikirnis", name: { ar: "ديكرنس", en: "Dikirnis" } }
    ]
  },
  {
    id: "red-sea",
    name: { ar: "البحر الأحمر", en: "Red Sea" },
    shippingCost: 120,
    cities: [
      { id: "hurghada", name: { ar: "الغردقة", en: "Hurghada" } },
      { id: "safaga", name: { ar: "سفاجا", en: "Safaga" } },
      { id: "quseer", name: { ar: "القصير", en: "Quseer" } },
      { id: "marsa-alam", name: { ar: "مرسى علم", en: "Marsa Alam" } },
      { id: "shalatin", name: { ar: "شلاتين", en: "Shalatin" } },
      { id: "halaib", name: { ar: "حلايب", en: "Halaib" } },
      { id: "abu-ramad", name: { ar: "أبو رماد", en: "Abu Ramad" } },
      { id: "ras-gharib", name: { ar: "رأس غارب", en: "Ras Gharib" } }
    ]
  },
  {
    id: "beheira",
    name: { ar: "البحيرة", en: "Beheira" },
    shippingCost: 70,
    cities: [
      { id: "damanhour", name: { ar: "دمنهور", en: "Damanhour" } },
      { id: "kafr-el-dawar", name: { ar: "كفر الدوار", en: "Kafr El Dawar" } },
      { id: "rashid", name: { ar: "رشيد", en: "Rashid" } },
      { id: "edko", name: { ar: "إدكو", en: "Edko" } },
      { id: "abu-el-matamer", name: { ar: "أبو المطامير", en: "Abu El Matamer" } },
      { id: "abu-homs", name: { ar: "أبو حمص", en: "Abu Homs" } },
      { id: "delengat", name: { ar: "الدلنجات", en: "Delengat" } },
      { id: "mahmoudiya", name: { ar: "المحمودية", en: "Mahmoudiya" } },
      { id: "rahmaniya", name: { ar: "الرحمانية", en: "Rahmaniya" } },
      { id: "kom-hamada", name: { ar: "كوم حمادة", en: "Kom Hamada" } },
      { id: "badr", name: { ar: "بدر", en: "Badr" } },
      { id: "wadi-natrun", name: { ar: "وادي النطرون", en: "Wadi Natrun" } },
      { id: "new-nubaria", name: { ar: "النوبارية الجديدة", en: "New Nubaria" } },
      { id: "itay-el-baroud", name: { ar: "إيتاي البارود", en: "Itay El Baroud" } },
      { id: "housh-eissa", name: { ar: "حوش عيسى", en: "Housh Eissa" } }
    ]
  },
  {
    id: "fayoum",
    name: { ar: "الفيوم", en: "Fayoum" },
    shippingCost: 75,
    cities: [
      { id: "fayoum-city", name: { ar: "الفيوم", en: "Fayoum City" } },
      { id: "ibsheway", name: { ar: "إبشواي", en: "Ibsheway" } },
      { id: "tamiya", name: { ar: "طامية", en: "Tamiya" } },
      { id: "snores", name: { ar: "سنورس", en: "Snores" } },
      { id: "itsa", name: { ar: "إطسا", en: "Itsa" } },
      { id: "yusuf-el-seddik", name: { ar: "يوسف الصديق", en: "Yusuf El Seddik" } }
    ]
  },
  {
    id: "gharbia",
    name: { ar: "الغربية", en: "Gharbia" },
    shippingCost: 65,
    cities: [
      { id: "tanta", name: { ar: "طنطا", en: "Tanta" } },
      { id: "mahalla-el-kobra", name: { ar: "المحلة الكبرى", en: "Mahalla El Kobra" } },
      { id: "kafr-el-zayat", name: { ar: "كفر الزيات", en: "Kafr El Zayat" } },
      { id: "zefta", name: { ar: "زفتى", en: "Zefta" } },
      { id: "santa", name: { ar: "سنتا", en: "Santa" } },
      { id: "qotour", name: { ar: "قطور", en: "Qotour" } },
      { id: "bassioun", name: { ar: "بسيون", en: "Bassioun" } },
      { id: "samanoud", name: { ar: "السمانود", en: "Samanoud" } }
    ]
  },
  {
    id: "ismailia",
    name: { ar: "الإسماعيلية", en: "Ismailia" },
    shippingCost: 70,
    cities: [
      { id: "ismailia-city", name: { ar: "الإسماعيلية", en: "Ismailia City" } },
      { id: "fayed", name: { ar: "فايد", en: "Fayed" } },
      { id: "qantara-east", name: { ar: "القنطرة شرق", en: "Qantara East" } },
      { id: "qantara-west", name: { ar: "القنطرة غرب", en: "Qantara West" } },
      { id: "abu-sweir", name: { ar: "أبو صوير", en: "Abu Sweir" } },
      { id: "kasasin", name: { ar: "القصاصين", en: "Kasasin" } },
      { id: "tel-el-kebir", name: { ar: "تل الكبير", en: "Tel El Kebir" } }
    ]
  },
  {
    id: "monufia",
    name: { ar: "المنوفية", en: "Monufia" },
    shippingCost: 65,
    cities: [
      { id: "shebin-el-kom", name: { ar: "شبين الكوم", en: "Shebin El Kom" } },
      { id: "menouf", name: { ar: "منوف", en: "Menouf" } },
      { id: "sers-el-lyan", name: { ar: "سرس الليان", en: "Sers El Lyan" } },
      { id: "ashmoun", name: { ar: "أشمون", en: "Ashmoun" } },
      { id: "el-bagour", name: { ar: "الباجور", en: "El Bagour" } },
      { id: "quesna", name: { ar: "قويسنا", en: "Quesna" } },
      { id: "berket-el-sabe", name: { ar: "بركة السبع", en: "Berket El Sabe" } },
      { id: "tala", name: { ar: "تلا", en: "Tala" } },
      { id: "el-shohada", name: { ar: "الشهداء", en: "El Shohada" } },
      { id: "sadat-city", name: { ar: "مدينة السادات", en: "Sadat City" } }
    ]
  },
  {
    id: "minya",
    name: { ar: "المنيا", en: "Minya" },
    shippingCost: 80,
    cities: [
      { id: "minya-city", name: { ar: "المنيا", en: "Minya City" } },
      { id: "mallawi", name: { ar: "ملوي", en: "Mallawi" } },
      { id: "beni-mazar", name: { ar: "بني مزار", en: "Beni Mazar" } },
      { id: "matay", name: { ar: "مطاي", en: "Matay" } },
      { id: "samalut", name: { ar: "سمالوط", en: "Samalut" } },
      { id: "maghagha", name: { ar: "مغاغة", en: "Maghagha" } },
      { id: "beni-hassan", name: { ar: "بني حسن", en: "Beni Hassan" } },
      { id: "abu-qurqas", name: { ar: "أبو قرقاص", en: "Abu Qurqas" } },
      { id: "deir-mawas", name: { ar: "دير مواس", en: "Deir Mawas" } }
    ]
  },
  {
    id: "qaliubiya",
    name: { ar: "القليوبية", en: "Qaliubiya" },
    shippingCost: 50,
    cities: [
      { id: "banha", name: { ar: "بنها", en: "Banha" } },
      { id: "qalyub", name: { ar: "قليوب", en: "Qalyub" } },
      { id: "shubra-el-kheima", name: { ar: "شبرا الخيمة", en: "Shubra El Kheima" } },
      { id: "el-qanater-el-khairiya", name: { ar: "القناطر الخيرية", en: "El Qanater El Khairiya" } },
      { id: "kafr-shukr", name: { ar: "كفر شكر", en: "Kafr Shukr" } },
      { id: "tukh", name: { ar: "طوخ", en: "Tukh" } },
      { id: "qaha", name: { ar: "قها", en: "Qaha" } },
      { id: "obour-city", name: { ar: "مدينة العبور", en: "Obour City" } },
      { id: "khosous", name: { ar: "الخصوص", en: "Khosous" } },
      { id: "khanka", name: { ar: "الخانكة", en: "Khanka" } }
    ]
  },
  {
    id: "new-valley",
    name: { ar: "الوادي الجديد", en: "New Valley" },
    shippingCost: 130,
    cities: [
      { id: "kharga", name: { ar: "الخارجة", en: "Kharga" } },
      { id: "dakhla", name: { ar: "الداخلة", en: "Dakhla" } },
      { id: "farafra", name: { ar: "الفرافرة", en: "Farafra" } },
      { id: "bahariya", name: { ar: "الباويطي", en: "Bahariya" } },
      { id: "balat", name: { ar: "بلاط", en: "Balat" } },
      { id: "paris", name: { ar: "باريس", en: "Paris" } }
    ]
  },
  {
    id: "suez",
    name: { ar: "السويس", en: "Suez" },
    shippingCost: 65,
    cities: [
      { id: "suez-city", name: { ar: "السويس", en: "Suez City" } },
      { id: "el-arbaeen", name: { ar: "الأربعين", en: "El Arbaeen" } },
      { id: "ataka", name: { ar: "عتاقة", en: "Ataka" } },
      { id: "el-ganayen", name: { ar: "الجناين", en: "El Ganayen" } },
      { id: "faisal", name: { ar: "فيصل", en: "Faisal" } }
    ]
  },
  {
    id: "aswan",
    name: { ar: "أسوان", en: "Aswan" },
    shippingCost: 100,
    cities: [
      { id: "aswan-city", name: { ar: "أسوان", en: "Aswan City" } },
      { id: "edfu", name: { ar: "إدفو", en: "Edfu" } },
      { id: "kom-ombo", name: { ar: "كوم أمبو", en: "Kom Ombo" } },
      { id: "daraw", name: { ar: "دراو", en: "Daraw" } },
      { id: "nasr-el-nuba", name: { ar: "نصر النوبة", en: "Nasr El Nuba" } },
      { id: "kalabsha", name: { ar: "كلابشة", en: "Kalabsha" } },
      { id: "abu-simbel", name: { ar: "أبو سمبل", en: "Abu Simbel" } }
    ]
  },
  {
    id: "assiut",
    name: { ar: "أسيوط", en: "Assiut" },
    shippingCost: 85,
    cities: [
      { id: "assiut-city", name: { ar: "أسيوط", en: "Assiut City" } },
      { id: "dayrut", name: { ar: "ديروط", en: "Dayrut" } },
      { id: "qusiya", name: { ar: "القوصية", en: "Qusiya" } },
      { id: "manfalut", name: { ar: "منفلوط", en: "Manfalut" } },
      { id: "abnoub", name: { ar: "أبنوب", en: "Abnoub" } },
      { id: "el-fateh", name: { ar: "الفتح", en: "El Fateh" } },
      { id: "sahel-seleem", name: { ar: "ساحل سليم", en: "Sahel Seleem" } },
      { id: "el-badari", name: { ar: "البداري", en: "El Badari" } },
      { id: "sidfa", name: { ar: "صدفا", en: "Sidfa" } },
      { id: "el-ghanayem", name: { ar: "الغنايم", en: "El Ghanayem" } },
      { id: "abu-tig", name: { ar: "أبو تيج", en: "Abu Tig" } }
    ]
  },
  {
    id: "beni-suef",
    name: { ar: "بني سويف", en: "Beni Suef" },
    shippingCost: 70,
    cities: [
      { id: "beni-suef-city", name: { ar: "بني سويف", en: "Beni Suef City" } },
      { id: "el-wasta", name: { ar: "الواسطى", en: "El Wasta" } },
      { id: "naser", name: { ar: "ناصر", en: "Naser" } },
      { id: "ihnasya", name: { ar: "إهناسيا", en: "Ihnasya" } },
      { id: "biba", name: { ar: "ببا", en: "Biba" } },
      { id: "fashn", name: { ar: "الفشن", en: "Fashn" } },
      { id: "somosta", name: { ar: "سمسطا", en: "Somosta" } },
      { id: "new-beni-suef", name: { ar: "بني سويف الجديدة", en: "New Beni Suef" } }
    ]
  },
  {
    id: "port-said",
    name: { ar: "بورسعيد", en: "Port Said" },
    shippingCost: 70,
    cities: [
      { id: "port-said-city", name: { ar: "بورسعيد", en: "Port Said City" } },
      { id: "port-fouad", name: { ar: "بور فؤاد", en: "Port Fouad" } },
      { id: "el-arab", name: { ar: "العرب", en: "El Arab" } },
      { id: "el-manakh", name: { ar: "المناخ", en: "El Manakh" } },
      { id: "el-zohour", name: { ar: "الزهور", en: "El Zohour" } },
      { id: "el-shark", name: { ar: "الشرق", en: "El Shark" } },
      { id: "el-dawahy", name: { ar: "الضواحي", en: "El Dawahy" } }
    ]
  },
  {
    id: "damietta",
    name: { ar: "دمياط", en: "Damietta" },
    shippingCost: 70,
    cities: [
      { id: "damietta-city", name: { ar: "دمياط", en: "Damietta City" } },
      { id: "new-damietta", name: { ar: "دمياط الجديدة", en: "New Damietta" } },
      { id: "ras-el-bar", name: { ar: "رأس البر", en: "Ras El Bar" } },
      { id: "faraskur", name: { ar: "فارسكور", en: "Faraskur" } },
      { id: "zarqa", name: { ar: "الزرقا", en: "Zarqa" } },
      { id: "kafr-saad", name: { ar: "كفر سعد", en: "Kafr Saad" } },
      { id: "kafr-el-batikh", name: { ar: "كفر البطيخ", en: "Kafr El Batikh" } }
    ]
  },
  {
    id: "sharkia",
    name: { ar: "الشرقية", en: "Sharkia" },
    shippingCost: 65,
    cities: [
      { id: "zagazig", name: { ar: "الزقازيق", en: "Zagazig" } },
      { id: "10th-ramadan", name: { ar: "العاشر من رمضان", en: "10th of Ramadan City" } },
      { id: "bilbeis", name: { ar: "بلبيس", en: "Bilbeis" } },
      { id: "minya-el-qamh", name: { ar: "منيا القمح", en: "Minya El Qamh" } },
      { id: "abu-hammad", name: { ar: "أبو حماد", en: "Abu Hammad" } },
      { id: "kafr-saqr", name: { ar: "كفر صقر", en: "Kafr Saqr" } },
      { id: "awlad-saqr", name: { ar: "أولاد صقر", en: "Awlad Saqr" } },
      { id: "el-huseiniya", name: { ar: "الحسينية", en: "El Huseiniya" } },
      { id: "abu-kebir", name: { ar: "أبو كبير", en: "Abu Kebir" } },
      { id: "faqous", name: { ar: "فاقوس", en: "Faqous" } },
      { id: "el-salihiya-el-gedida", name: { ar: "الصالحية الجديدة", en: "El Salihiya El Gedida" } },
      { id: "deirb-negm", name: { ar: "ديرب نجم", en: "Deirb Negm" } },
      { id: "mashtool-el-souk", name: { ar: "مشتول السوق", en: "Mashtool El Souk" } }
    ]
  },
  {
    id: "south-sinai",
    name: { ar: "جنوب سيناء", en: "South Sinai" },
    shippingCost: 110,
    cities: [
      { id: "sharm-el-sheikh", name: { ar: "شرم الشيخ", en: "Sharm El Sheikh" } },
      { id: "dahab", name: { ar: "دهب", en: "Dahab" } },
      { id: "nuweiba", name: { ar: "نويبع", en: "Nuweiba" } },
      { id: "taba", name: { ar: "طابا", en: "Taba" } },
      { id: "saint-catherine", name: { ar: "سانت كاترين", en: "Saint Catherine" } },
      { id: "abu-zenima", name: { ar: "أبو زنيمة", en: "Abu Zenima" } },
      { id: "abu-rudeis", name: { ar: "أبو رديس", en: "Abu Rudeis" } },
      { id: "ras-sedr", name: { ar: "رأس سدر", en: "Ras Sedr" } },
      { id: "el-tor", name: { ar: "الطور", en: "El Tor" } }
    ]
  },
  {
    id: "kafr-el-sheikh",
    name: { ar: "كفر الشيخ", en: "Kafr El Sheikh" },
    shippingCost: 70,
    cities: [
      { id: "kafr-el-sheikh-city", name: { ar: "كفر الشيخ", en: "Kafr El Sheikh City" } },
      { id: "desouk", name: { ar: "دسوق", en: "Desouk" } },
      { id: "fooh", name: { ar: "فوه", en: "Fooh" } },
      { id: "metobas", name: { ar: "مطوبس", en: "Metobas" } },
      { id: "burg-el-borollos", name: { ar: "برج البرلس", en: "Burg El Borollos" } },
      { id: "baltim", name: { ar: "بلطيم", en: "Baltim" } },
      { id: "hamoul", name: { ar: "الحامول", en: "Hamoul" } },
      { id: "biyala", name: { ar: "بيلا", en: "Biyala" } },
      { id: "riyadh", name: { ar: "الرياض", en: "Riyadh" } },
      { id: "sidi-salem", name: { ar: "سيدي سالم", en: "Sidi Salem" } }
    ]
  },
  {
    id: "matrouh",
    name: { ar: "مطروح", en: "Matrouh" },
    shippingCost: 100,
    cities: [
      { id: "marsa-matrouh", name: { ar: "مرسى مطروح", en: "Marsa Matrouh" } },
      { id: "el-alamein", name: { ar: "العلمين", en: "El Alamein" } },
      { id: "el-dabaa", name: { ar: "الضبعة", en: "El Dabaa" } },
      { id: "el-hamam", name: { ar: "الحمام", en: "El Hamam" } },
      { id: "sidi-abdel-rahman", name: { ar: "سيدي عبد الرحمن", en: "Sidi Abdel Rahman" } },
      { id: "salloum", name: { ar: "السلوم", en: "Salloum" } },
      { id: "siwa", name: { ar: "سيوة", en: "Siwa" } },
      { id: "barani", name: { ar: "براني", en: "Barani" } }
    ]
  },
  {
    id: "luxor",
    name: { ar: "الأقصر", en: "Luxor" },
    shippingCost: 95,
    cities: [
      { id: "luxor-city", name: { ar: "الأقصر", en: "Luxor City" } },
      { id: "esna", name: { ar: "إسنا", en: "Esna" } },
      { id: "armant", name: { ar: "أرمنت", en: "Armant" } },
      { id: "el-tod", name: { ar: "الطود", en: "El Tod" } },
      { id: "el-zeiniya", name: { ar: "الزينية", en: "El Zeiniya" } },
      { id: "el-qurna", name: { ar: "القرنة", en: "El Qurna" } },
      { id: "new-luxor", name: { ar: "الأقصر الجديدة", en: "New Luxor" } }
    ]
  },
  {
    id: "qena",
    name: { ar: "قنا", en: "Qena" },
    shippingCost: 90,
    cities: [
      { id: "qena-city", name: { ar: "قنا", en: "Qena City" } },
      { id: "nag-hammadi", name: { ar: "نجع حمادي", en: "Nag Hammadi" } },
      { id: "dishna", name: { ar: "دشنا", en: "Dishna" } },
      { id: "abu-tesht", name: { ar: "أبو تشت", en: "Abu Tesht" } },
      { id: "farshut", name: { ar: "فرشوط", en: "Farshut" } },
      { id: "naqada", name: { ar: "نقادة", en: "Naqada" } },
      { id: "qift", name: { ar: "قفط", en: "Qift" } },
      { id: "qus", name: { ar: "قوص", en: "Qus" } },
      { id: "el-waqf", name: { ar: "الوقف", en: "El Waqf" } }
    ]
  },
  {
    id: "north-sinai",
    name: { ar: "شمال سيناء", en: "North Sinai" },
    shippingCost: 100,
    cities: [
      { id: "el-arish", name: { ar: "العريش", en: "El Arish" } },
      { id: "rafah", name: { ar: "رفح", en: "Rafah" } },
      { id: "sheikh-zuweid", name: { ar: "الشيخ زويد", en: "Sheikh Zuweid" } },
      { id: "bir-el-abd", name: { ar: "بئر العبد", en: "Bir El Abd" } },
      { id: "hasana", name: { ar: "حسنة", en: "Hasana" } },
      { id: "nakhl", name: { ar: "نخل", en: "Nakhl" } },
      { id: "el-qantara-shark", name: { ar: "القنطرة شرق", en: "El Qantara Shark" } }
    ]
  },
  {
    id: "sohag",
    name: { ar: "سوهاج", en: "Sohag" },
    shippingCost: 85,
    cities: [
      { id: "sohag-city", name: { ar: "سوهاج", en: "Sohag City" } },
      { id: "akhmim", name: { ar: "أخميم", en: "Akhmim" } },
      { id: "el-balyana", name: { ar: "البلينا", en: "El Balyana" } },
      { id: "el-maragha", name: { ar: "المراغة", en: "El Maragha" } },
      { id: "el-monsha", name: { ar: "المنشأة", en: "El Monsha" } },
      { id: "dar-el-salam", name: { ar: "دار السلام", en: "Dar El Salam" } },
      { id: "juhayna", name: { ar: "جهينة", en: "Juhayna" } },
      { id: "saqulta", name: { ar: "ساقلتة", en: "Saqulta" } },
      { id: "gerga", name: { ar: "جرجا", en: "Gerga" } },
      { id: "el-usairat", name: { ar: "العسيرات", en: "El Usairat" } },
      { id: "tema", name: { ar: "طما", en: "Tema" } }
    ]
  }
];

export const getGovernorateById = (id: string): Governorate | undefined => {
  return egyptData.find(gov => gov.id === id);
};

export const getCityById = (governorateId: string, cityId: string): City | undefined => {
  const governorate = getGovernorateById(governorateId);
  return governorate?.cities.find(city => city.id === cityId);
};

export const getShippingCost = (governorateId: string): number => {
  const governorate = getGovernorateById(governorateId);
  return governorate?.shippingCost || 60; // Default shipping cost
};
