import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { FiMapPin, FiChevronDown, FiSearch } from 'react-icons/fi';
import Fuse from 'fuse.js';
import { useLang } from '../contexts/LangContext';
import { egyptData, getGovernorateById, getCityById, getShippingCost } from '../data/egyptData';
import { AddressSelectorProps, ShippingAddress } from '../types';
import ErrorMessage from './ErrorMessage';

export default function AddressSelector({ 
  onAddressChange, 
  selectedGovernorate, 
  selectedCity, 
  detailedAddress = '',
  className = '',
  errors = {}
}: AddressSelectorProps) {
  const { lang } = useLang();
  const [governorate, setGovernorate] = useState(selectedGovernorate || '');
  const [city, setCity] = useState(selectedCity || '');
  const [address, setAddress] = useState(detailedAddress);
  const [isGovernorateOpen, setIsGovernorateOpen] = useState(false);
  const [isCityOpen, setIsCityOpen] = useState(false);
  const [governorateSearch, setGovernorateSearch] = useState('');
  const [citySearch, setCitySearch] = useState('');

  const selectedGovData = governorate ? getGovernorateById(governorate) : null;
  const availableCities = selectedGovData?.cities || [];

  // Fuzzy search configuration with Arabic text normalization
  const normalizeArabicText = (text: string) => {
    return text
      .replace(/[أإآ]/g, 'ا') // Normalize Alef variations
      .replace(/[ة]/g, 'ه') // Normalize Taa Marbouta
      .replace(/[ى]/g, 'ي') // Normalize Yaa variations
      .replace(/[ئ]/g, 'ي') // Normalize Hamza on Yaa
      .replace(/[ؤ]/g, 'و') // Normalize Hamza on Waw
      .replace(/[\u064B-\u0652]/g, '') // Remove diacritics
      .trim();
  };

  // Create searchable data with normalized text
  const searchableGovernorates = egyptData.map(gov => ({
    ...gov,
    searchText: `${normalizeArabicText(gov.name.ar)} ${gov.name.en.toLowerCase()}`
  }));

  const searchableCities = availableCities.map(city => ({
    ...city,
    searchText: `${normalizeArabicText(city.name.ar)} ${city.name.en.toLowerCase()}`
  }));

  const governorateFuse = new Fuse(searchableGovernorates, {
    keys: ['name.ar', 'name.en', 'searchText'],
    threshold: 0.4, // More tolerant for Arabic variations
    distance: 200,
    minMatchCharLength: 1,
    includeScore: true,
    ignoreLocation: true
  });

  const cityFuse = new Fuse(searchableCities, {
    keys: ['name.ar', 'name.en', 'searchText'],
    threshold: 0.4,
    distance: 200,
    minMatchCharLength: 1,
    includeScore: true,
    ignoreLocation: true
  });

  // Filter data based on search with normalized input
  const filteredGovernorates = governorateSearch.trim() 
    ? governorateFuse.search(normalizeArabicText(governorateSearch)).map(result => ({
        id: result.item.id,
        name: result.item.name,
        shippingCost: result.item.shippingCost,
        cities: result.item.cities
      }))
    : egyptData;

  const filteredCities = citySearch.trim()
    ? cityFuse.search(normalizeArabicText(citySearch)).map(result => ({
        id: result.item.id,
        name: result.item.name
      }))
    : availableCities;

  // Update parent component when address changes
  useEffect(() => {
    if (governorate) {
      const govData = getGovernorateById(governorate);
      
      if (govData) {
        // Create partial address with shipping cost even if city/address not complete
        const shippingAddress: ShippingAddress = {
          governorate,
          governorateName: govData.name,
          city: city || '',
          cityName: city ? getCityById(governorate, city)?.name || { ar: '', en: '' } : { ar: '', en: '' },
          detailedAddress: address,
          shippingCost: getShippingCost(governorate)
        };
        
        // Only pass complete address if all required fields are filled
        if (city && address.trim()) {
          const cityData = getCityById(governorate, city);
          if (cityData) {
            shippingAddress.cityName = cityData.name;
            onAddressChange(shippingAddress);
          }
        } else {
          // Pass partial address for shipping cost calculation
          onAddressChange(shippingAddress);
        }
      }
    } else {
      onAddressChange(null);
    }
  }, [governorate, city, address, onAddressChange]);

  const handleGovernorateChange = (govId: string) => {
    setGovernorate(govId);
    setCity(''); // Reset city when governorate changes
    setIsGovernorateOpen(false);
    setGovernorateSearch(''); // Clear search
  };

  const handleCityChange = (cityId: string) => {
    setCity(cityId);
    setIsCityOpen(false);
    setCitySearch(''); // Clear search
  };

  const handleGovernorateToggle = () => {
    setIsGovernorateOpen(!isGovernorateOpen);
    if (!isGovernorateOpen) {
      setGovernorateSearch(''); // Clear search when opening
    }
  };

  const handleCityToggle = () => {
    setIsCityOpen(!isCityOpen);
    if (!isCityOpen) {
      setCitySearch(''); // Clear search when opening
    }
  };

  const getPlaceholder = (type: 'governorate' | 'city' | 'address') => {
    const placeholders = {
      governorate: {
        ar: 'اختر المحافظة',
        en: 'Select Governorate'
      },
      city: {
        ar: 'اختر المدينة/المركز',
        en: 'Select City/Center'
      },
      address: {
        ar: 'أدخل العنوان التفصيلي (الشارع، المبنى، الدور، الشقة، علامات مميزة)',
        en: 'Enter detailed address (street, building, floor, apartment, landmarks)'
      }
    };
    return placeholders[type][lang as keyof typeof placeholders[typeof type]];
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Governorate Dropdown */}
      <div>
        <label className={`block text-sm font-semibold mb-2 ${errors.governorate ? 'text-red-600' : 'text-gray-700'}`}>
          <FiMapPin className="inline mr-2" />
          {lang === 'ar' ? 'المحافظة' : 'Governorate'}
          <span className="text-red-500 mr-1">*</span>
        </label>
        <div className="relative">
          <button
            type="button"
            onClick={handleGovernorateToggle}
            className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 flex items-center justify-between transition-all ${
              errors.governorate 
                ? 'border-red-500 focus:ring-red-500 bg-red-50/50'
                : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
            } ${isGovernorateOpen ? 'ring-2' : ''}`}
          >
            <span className={selectedGovData ? 'text-gray-900' : 'text-gray-500'}>
              {selectedGovData ? selectedGovData.name[lang as keyof typeof selectedGovData.name] : getPlaceholder('governorate')}
            </span>
            <FiChevronDown className={`transform transition-transform ${isGovernorateOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {isGovernorateOpen && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute z-50 w-full mt-1 glass border border-[#d1b16a]/40 rounded-xl shadow-lg max-h-80 overflow-hidden"
              onWheel={(e) => e.stopPropagation()}
            >
              {/* Search Input */}
              <div className="p-3 border-b border-gray-200">
                <div className="relative">
                  <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={governorateSearch}
                    onChange={(e) => setGovernorateSearch(e.target.value)}
                    placeholder={lang === 'ar' ? 'ابحث عن المحافظة...' : 'Search governorate...'}
                    className="w-full pl-10 pr-4 py-2 glass border border-[#d1b16a]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#d1b16a] text-sm"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>
              
              {/* Governorate List */}
              <div className="max-h-48 overflow-y-auto">
                {filteredGovernorates.length > 0 ? (
                  filteredGovernorates.map((gov) => (
                <button
                  key={gov.id}
                  type="button"
                  onClick={() => handleGovernorateChange(gov.id)}
                  className={`w-full px-4 py-3 text-left hover:bg-[#d1b16a]/10 transition-colors border-b border-gray-100 last:border-b-0 ${
                    governorate === gov.id ? 'bg-[#d1b16a]/20 text-[#d1b16a] font-semibold' : ''
                  }`}
                >
                  <div className="flex justify-between items-center">
                    <span>{gov.name[lang as keyof typeof gov.name]}</span>
                    <span className="text-sm text-gray-500">{gov.shippingCost} {lang === 'ar' ? 'ج.م' : 'EGP'}</span>
                    </div>
                  </button>
                  ))
                ) : (
                  <div className="px-4 py-3 text-center text-gray-500 text-sm">
                    {lang === 'ar' ? 'لا توجد نتائج' : 'No results found'}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>
        <ErrorMessage error={errors.governorate} />
      </div>

      {/* City Dropdown */}
      <div>
        <label className={`block text-sm font-semibold mb-2 ${errors.city ? 'text-red-600' : 'text-gray-700'}`}>
          <FiMapPin className="inline mr-2" />
          {lang === 'ar' ? 'المدينة/المركز' : 'City/Center'}
          <span className="text-red-500 mr-1">*</span>
        </label>
        <div className="relative">
          <button
            type="button"
            disabled={!governorate}
            onClick={handleCityToggle}
            className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 flex items-center justify-between transition-all ${
              !governorate ? 'opacity-50 cursor-not-allowed' : ''
            } ${
              errors.city 
                ? 'border-red-500 focus:ring-red-500 bg-red-50/50'
                : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
            } ${isCityOpen ? 'ring-2' : ''}`}
          >
            <span className={city && selectedGovData ? 'text-gray-900' : 'text-gray-500'}>
              {city && selectedGovData 
                ? getCityById(governorate, city)?.name[lang as 'ar' | 'en'] 
                : getPlaceholder('city')
              }
            </span>
            <FiChevronDown className={`transform transition-transform ${isCityOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {isCityOpen && governorate && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute z-40 w-full mt-1 glass border border-[#d1b16a]/40 rounded-xl shadow-lg max-h-80 overflow-hidden"
              onWheel={(e) => e.stopPropagation()}
            >
              {/* Search Input */}
              <div className="p-3 border-b border-gray-200">
                <div className="relative">
                  <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                  <input
                    type="text"
                    value={citySearch}
                    onChange={(e) => setCitySearch(e.target.value)}
                    placeholder={lang === 'ar' ? 'ابحث عن المدينة/المركز...' : 'Search city/center...'}
                    className="w-full pl-10 pr-4 py-2 glass border border-[#d1b16a]/30 rounded-lg focus:outline-none focus:ring-2 focus:ring-[#d1b16a] text-sm"
                    onClick={(e) => e.stopPropagation()}
                  />
                </div>
              </div>
              
              {/* City List */}
              <div className="max-h-48 overflow-y-auto">
                {filteredCities.length > 0 ? (
                  filteredCities.map((cityData) => (
                <button
                  key={cityData.id}
                  type="button"
                  onClick={() => handleCityChange(cityData.id)}
                  className={`w-full px-4 py-3 text-left hover:bg-[#d1b16a]/10 transition-colors border-b border-gray-100 last:border-b-0 ${
                    city === cityData.id ? 'bg-[#d1b16a]/20 text-[#d1b16a] font-semibold' : ''
                  }`}
                  >
                    {cityData.name[lang as keyof typeof cityData.name]}
                  </button>
                  ))
                ) : (
                  <div className="px-4 py-3 text-center text-gray-500 text-sm">
                    {lang === 'ar' ? 'لا توجد نتائج' : 'No results found'}
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </div>
        <ErrorMessage error={errors.city} />
      </div>

      {/* Detailed Address */}
      <div>
        <label className={`block text-sm font-semibold mb-2 ${errors.detailedAddress ? 'text-red-600' : 'text-gray-700'}`}>
          <FiMapPin className="inline mr-2" />
          {lang === 'ar' ? 'العنوان التفصيلي' : 'Detailed Address'}
          <span className="text-red-500 mr-1">*</span>
        </label>
        <textarea
          rows={4}
          value={address}
          onChange={(e) => setAddress(e.target.value)}
          className={`w-full glass border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 resize-none min-w-0 transition-colors ${
            errors.detailedAddress 
              ? 'border-red-500 focus:ring-red-500 bg-red-50/50'
              : 'border-[#d1b16a]/40 focus:ring-[#d1b16a]'
          }`}
          placeholder={getPlaceholder('address')}
        />
        <ErrorMessage error={errors.detailedAddress} />
      </div>

      {/* Shipping Cost Display */}
      {selectedGovData && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass p-4 rounded-xl bg-[#d1b16a]/10 border border-[#d1b16a]/30"
        >
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium text-gray-700">
              {lang === 'ar' ? 'تكلفة الشحن إلى' : 'Shipping cost to'} {selectedGovData.name[lang as keyof typeof selectedGovData.name]}:
            </span>
            <span className="text-lg font-bold text-[#d1b16a]">
              {selectedGovData.shippingCost} {lang === 'ar' ? 'ج.م' : 'EGP'}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}
