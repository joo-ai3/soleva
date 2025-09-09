from django.core.management.base import BaseCommand
from shipping.models import Governorate, City


class Command(BaseCommand):
    help = 'Load Egypt governorates and cities data'
    
    def handle(self, *args, **options):
        # Egypt governorates data
        governorates_data = [
            {'name_en': 'Cairo', 'name_ar': 'القاهرة', 'code': 'CAI'},
            {'name_en': 'Giza', 'name_ar': 'الجيزة', 'code': 'GIZ'},
            {'name_en': 'Alexandria', 'name_ar': 'الإسكندرية', 'code': 'ALX'},
            {'name_en': 'Dakahlia', 'name_ar': 'الدقهلية', 'code': 'DK'},
            {'name_en': 'Red Sea', 'name_ar': 'البحر الأحمر', 'code': 'BA'},
            {'name_en': 'Beheira', 'name_ar': 'البحيرة', 'code': 'BH'},
            {'name_en': 'Fayoum', 'name_ar': 'الفيوم', 'code': 'FYM'},
            {'name_en': 'Gharbiya', 'name_ar': 'الغربية', 'code': 'GH'},
            {'name_en': 'Ismailia', 'name_ar': 'الإسماعيلية', 'code': 'IS'},
            {'name_en': 'Menofia', 'name_ar': 'المنوفية', 'code': 'MN'},
            {'name_en': 'Minya', 'name_ar': 'المنيا', 'code': 'MNY'},
            {'name_en': 'Qaliubiya', 'name_ar': 'القليوبية', 'code': 'KB'},
            {'name_en': 'New Valley', 'name_ar': 'الوادي الجديد', 'code': 'WAD'},
            {'name_en': 'Suez', 'name_ar': 'السويس', 'code': 'SUZ'},
            {'name_en': 'Aswan', 'name_ar': 'أسوان', 'code': 'ASN'},
            {'name_en': 'Assiut', 'name_ar': 'أسيوط', 'code': 'AST'},
            {'name_en': 'Beni Suef', 'name_ar': 'بني سويف', 'code': 'BNS'},
            {'name_en': 'Port Said', 'name_ar': 'بورسعيد', 'code': 'PTS'},
            {'name_en': 'Damietta', 'name_ar': 'دمياط', 'code': 'DT'},
            {'name_en': 'Sharkia', 'name_ar': 'الشرقية', 'code': 'SHR'},
            {'name_en': 'South Sinai', 'name_ar': 'جنوب سيناء', 'code': 'JS'},
            {'name_en': 'Kafr El Sheikh', 'name_ar': 'كفر الشيخ', 'code': 'KFS'},
            {'name_en': 'Matrouh', 'name_ar': 'مطروح', 'code': 'MT'},
            {'name_en': 'Luxor', 'name_ar': 'الأقصر', 'code': 'LX'},
            {'name_en': 'Qena', 'name_ar': 'قنا', 'code': 'KN'},
            {'name_en': 'North Sinai', 'name_ar': 'شمال سيناء', 'code': 'SIN'},
            {'name_en': 'Sohag', 'name_ar': 'سوهاج', 'code': 'SHG'},
        ]
        
        # Cities data (sample for major governorates)
        cities_data = {
            'CAI': [  # Cairo
                {'name_en': 'Nasr City', 'name_ar': 'مدينة نصر'},
                {'name_en': 'Heliopolis', 'name_ar': 'مصر الجديدة'},
                {'name_en': 'Maadi', 'name_ar': 'المعادي'},
                {'name_en': 'Zamalek', 'name_ar': 'الزمالك'},
                {'name_en': 'Downtown', 'name_ar': 'وسط البلد'},
                {'name_en': 'Shubra', 'name_ar': 'شبرا'},
                {'name_en': 'Ain Shams', 'name_ar': 'عين شمس'},
                {'name_en': 'Helwan', 'name_ar': 'حلوان'},
                {'name_en': 'New Cairo', 'name_ar': 'القاهرة الجديدة'},
            ],
            'GIZ': [  # Giza
                {'name_en': 'Dokki', 'name_ar': 'الدقي'},
                {'name_en': 'Mohandessin', 'name_ar': 'المهندسين'},
                {'name_en': 'Agouza', 'name_ar': 'العجوزة'},
                {'name_en': 'Haram', 'name_ar': 'الهرم'},
                {'name_en': '6th of October', 'name_ar': '6 أكتوبر'},
                {'name_en': 'Sheikh Zayed', 'name_ar': 'الشيخ زايد'},
            ],
            'ALX': [  # Alexandria
                {'name_en': 'Sporting', 'name_ar': 'سبورتنج'},
                {'name_en': 'Stanley', 'name_ar': 'ستانلي'},
                {'name_en': 'Sidi Gaber', 'name_ar': 'سيدي جابر'},
                {'name_en': 'Raml Station', 'name_ar': 'محطة الرمل'},
                {'name_en': 'Smouha', 'name_ar': 'سموحة'},
                {'name_en': 'Miami', 'name_ar': 'ميامي'},
            ],
        }
        
        self.stdout.write('Loading governorates...')
        
        for gov_data in governorates_data:
            governorate, created = Governorate.objects.get_or_create(
                code=gov_data['code'],
                defaults=gov_data
            )
            if created:
                self.stdout.write(f'Created governorate: {governorate.name_en}')
            
            # Load cities for this governorate
            if gov_data['code'] in cities_data:
                self.stdout.write(f'Loading cities for {governorate.name_en}...')
                for city_data in cities_data[gov_data['code']]:
                    city, created = City.objects.get_or_create(
                        governorate=governorate,
                        name_en=city_data['name_en'],
                        defaults=city_data
                    )
                    if created:
                        self.stdout.write(f'  Created city: {city.name_en}')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {Governorate.objects.count()} governorates '
                f'and {City.objects.count()} cities'
            )
        )
