import React, { useState } from 'react';
import { FiUser, FiFileText, FiBox, FiMapPin, FiLogOut, FiEdit3, FiSave, FiMessageCircle } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import { useLang, useTranslation } from '../contexts/LangContext';

import GlassButton from '../components/GlassButton';
import UserMessagesInbox from '../components/UserMessagesInbox';

export default function AccountPage() {
  const { user, logout } = useAuth();
  const { lang } = useLang();
  const t = useTranslation();
  const [tab, setTab] = useState("profile");
  const [editMode, setEditMode] = useState(false);
  const [userData, setUserData] = useState({
    name: user?.name || "",
    email: user?.email || ""
  });

  if (!user) {
    return (
      <div className="container mx-auto py-20 text-center text-2xl text-red-500">
        {t("mustLoginCheckout")}
      </div>
    );
  }

  const tabs = [
    { key: "profile", icon: <FiUser />, label: t("account") },
    { key: "messages", icon: <FiMessageCircle />, label: lang === 'ar' ? 'الرسائل' : 'Messages' },
    { key: "orders", icon: <FiFileText />, label: t("orders") },
    { key: "tracking", icon: <FiBox />, label: t("trackOrders") },
    { key: "addresses", icon: <FiMapPin />, label: t("addresses") },
  ];

  function handleSave() {
    setEditMode(false);
    // Here you would typically save to backend
  }

  return (
    <div className="container mx-auto py-10 px-4 max-w-4xl">
      <div className="glass p-4 md:p-8 rounded-2xl shadow-xl">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <aside className="account-sidebar lg:w-64 hidden lg:block">
            <div className="space-y-2 mb-8">
              {tabs.map(item => (
                <button
                  key={item.key}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-semibold transition-all ${
                    tab === item.key 
                      ? "bg-[#d1b16a] text-black shadow-lg" 
                      : "hover:bg-[#d1b16a]/20 text-gray-700"
                  }`}
                  onClick={() => setTab(item.key)}
                >
                  {item.icon} {item.label}
                </button>
              ))}
            </div>
            
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl hover:bg-red-100 text-red-600 font-semibold transition-all"
            >
              <FiLogOut /> {t("logout")}
            </button>
          </aside>

          {/* Mobile Navigation */}
          <div className="lg:hidden mb-6">
            <div className="flex flex-col gap-3">
            {tabs.map(item => (
              <button
                key={item.key}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-semibold transition-all ${
                  tab === item.key 
                    ? "bg-[#d1b16a] text-black shadow-lg" 
                    : "glass text-gray-700 hover:bg-[#d1b16a]/20"
                }`}
                onClick={() => setTab(item.key)}
              >
                {item.icon} {item.label}
              </button>
            ))}
            <button
              onClick={logout}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-xl glass hover:bg-red-100 text-red-600 font-semibold transition-all"
            >
              <FiLogOut /> {t("logout")}
            </button>
            </div>
          </div>

          {/* Main Content */}
          <main className="flex-1">
            {tab === "profile" && (
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold">{t("account")}</h2>
                  <GlassButton
                    onClick={() => editMode ? handleSave() : setEditMode(true)}
                    className="px-4 py-2"
                  >
                    {editMode ? <FiSave /> : <FiEdit3 />}
                    {editMode ? t("save") : t("edit")}
                  </GlassButton>
                </div>
                
                {!editMode ? (
                  <div className="space-y-4">
                    <div className="glass p-4 rounded-xl">
                      <label className="block text-sm font-semibold text-gray-600 mb-1">
                        {t("name")}
                      </label>
                      <div className="text-lg">{userData.name}</div>
                    </div>
                    <div className="glass p-4 rounded-xl">
                      <label className="block text-sm font-semibold text-gray-600 mb-1">
                        {t("email")}
                      </label>
                      <div className="text-lg">{userData.email}</div>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        {t("name")}
                      </label>
                      <input
                        className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3"
                        value={userData.name}
                        onChange={e => setUserData({...userData, name: e.target.value})}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        {t("email")}
                      </label>
                      <input
                        type="email"
                        className="w-full glass border border-[#d1b16a]/40 rounded-xl px-4 py-3"
                        value={userData.email}
                        onChange={e => setUserData({...userData, email: e.target.value})}
                      />
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {tab === "messages" && (
              <div>
                <UserMessagesInbox />
              </div>
            )}
            
            {tab === "orders" && (
              <div>
                <h2 className="text-2xl font-bold mb-6">{t("orders")}</h2>
                <div className="text-center py-12 text-gray-500">
                  <FiFileText size={48} className="mx-auto mb-4 opacity-50" />
                  <p>{t("ordersPlaceholder")}</p>
                </div>
              </div>
            )}
            
            {tab === "tracking" && (
              <div>
                <h2 className="text-2xl font-bold mb-6">{t("orderTracking")}</h2>
                <div className="text-center py-12 text-gray-500">
                  <FiBox size={48} className="mx-auto mb-4 opacity-50" />
                  <p>{t("orderTrackingPlaceholder")}</p>
                </div>
              </div>
            )}
            
            {tab === "addresses" && (
              <div>
                <h2 className="text-2xl font-bold mb-6">{t("addresses")}</h2>
                <div className="text-center py-12 text-gray-500">
                  <FiMapPin size={48} className="mx-auto mb-4 opacity-50" />
                  <p>{lang === "ar" ? "قريبًا إدارة العناوين..." : "Address management coming soon..."}</p>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}