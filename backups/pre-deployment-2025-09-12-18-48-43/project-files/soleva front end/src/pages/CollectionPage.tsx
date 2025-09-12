import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useLang, useTranslation } from '../contexts/LangContext';
import { collections, products } from '../data/products';

export default function CollectionPage() {
  const { id } = useParams();
  const { lang } = useLang();
  const t = useTranslation();
  const collection = collections.find((c) => c.id === id);
  const filtered = products.filter((p) => p.collection === id);

  if (!collection) {
    return (
      <div className="container mx-auto py-20 text-center text-2xl text-red-500">
        {t("notfound")}
      </div>
    );
  }

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="mb-8 flex items-center gap-4">
        <img 
          src={collection.image} 
          alt={collection.name[lang]} 
          className="w-28 h-28 object-cover rounded-2xl" 
        />
        <div>
          <div className="text-3xl font-bold mb-1">{collection.name[lang]}</div>
          <div className="text-[#666]">{collection.desc[lang]}</div>
        </div>
      </div>
      
      {filtered.length === 0 && (
        <div className="text-center text-gray-500 py-10">{t("productNotFound")}</div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {filtered.map((prod) => (
          <Link to={`/product/${prod.id}`} key={prod.id}>
            <div className="glass p-6 rounded-2xl shadow-xl border border-white/25 group hover:shadow-2xl transition-all">
              <img 
                src={prod.image} 
                className="w-full h-40 object-cover rounded-xl mb-3 group-hover:scale-110 transition" 
              />
              <div className="font-bold text-lg">{prod.name[lang]}</div>
              <div className="text-[#d1b16a] font-bold">{prod.price} {t("egp")}</div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}