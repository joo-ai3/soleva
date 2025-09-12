import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import { FiUser, FiLock, FiLogIn, FiEye, FiEyeOff } from 'react-icons/fi';
import { useAuth } from '../contexts/AuthContext';
import { useToast } from '../contexts/ToastContext';

import { useLang, useTranslation } from '../contexts/LangContext';
import GlassCard from '../components/GlassCard';
import GlassButton from '../components/GlassButton';

export default function LoginPage() {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const { lang } = useLang();
  const t = useTranslation();
  
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  function validateForm() {
    const newErrors: Record<string, string> = {};
    
    if (!email) {
      newErrors.email = t("requiredField");
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = lang === "ar" ? "البريد الإلكتروني غير صحيح" : "Invalid email format";
    }
    
    if (!password) {
      newErrors.password = t("requiredField");
    } else if (password.length < 6) {
      newErrors.password = lang === "ar" ? "كلمة المرور يجب أن تكون 6 أحرف على الأقل" : "Password must be at least 6 characters";
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setIsLoading(true);
    
    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      login({ name: email.split('@')[0], email });
      showToast(t("loginSuccess"));
      navigate("/account");
    } catch {
      showToast(lang === "ar" ? "حدث خطأ أثناء تسجيل الدخول" : "Login failed");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="container mx-auto py-10 px-4">
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.7, ease: [0.4, 0, 0.2, 1] }}
        className="max-w-md mx-auto"
      >
        <GlassCard>
          <div className="text-center mb-8">
            <motion.div 
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.3, duration: 0.5, type: "spring", stiffness: 200 }}
              className="w-20 h-20 bg-[#d1b16a]/20 rounded-full flex items-center justify-center mx-auto mb-4"
            >
              <FiLogIn size={32} className="text-[#d1b16a]" />
            </motion.div>
            <h1 className="text-3xl font-bold mb-2 text-[#111]">{t("login")}</h1>
            <p className="text-gray-600">
              {lang === "ar" ? "مرحباً بعودتك إلى سوليفا" : "Welcome back to Soleva"}
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Field */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t("email")}
              </label>
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                  <FiUser size={20} />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={e => {
                    setEmail(e.target.value);
                    if (errors.email) setErrors({...errors, email: ""});
                  }}
                  className={`w-full glass border rounded-xl px-12 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] transition-all ${
                    errors.email ? 'border-red-400' : 'border-[#d1b16a]/40'
                  }`}
                  placeholder={lang === "ar" ? "أدخل بريدك الإلكتروني" : "Enter your email"}
                />
              </div>
              {errors.email && (
                <p className="text-red-500 text-sm mt-1">{errors.email}</p>
              )}
            </div>

            {/* Password Field */}
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">
                {t("password")}
              </label>
              <div className="relative">
                <div className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
                  <FiLock size={20} />
                </div>
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={e => {
                    setPassword(e.target.value);
                    if (errors.password) setErrors({...errors, password: ""});
                  }}
                  className={`w-full glass border rounded-xl px-12 py-3 focus:outline-none focus:ring-2 focus:ring-[#d1b16a] transition-all ${
                    errors.password ? 'border-red-400' : 'border-[#d1b16a]/40'
                  }`}
                  placeholder={lang === "ar" ? "أدخل كلمة المرور" : "Enter your password"}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <FiEyeOff size={20} /> : <FiEye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p className="text-red-500 text-sm mt-1">{errors.password}</p>
              )}
            </div>

            <GlassButton 
              type="submit" 
              className="w-full bg-[#d1b16a] text-black border-none hover:bg-[#d1b16a]/80 min-h-[52px] font-bold hover:scale-105 transition-all duration-300"
              disabled={isLoading}
            >
              {isLoading ? (
                <div className="w-6 h-6 border-2 border-black/20 border-t-black rounded-full animate-spin" />
              ) : (
                <>
                  <FiLogIn />
                  {t("login")}
                </>
              )}
            </GlassButton>
          </form>

          <div className="mt-8 text-center">
            <p className="text-gray-600">
              {t("dontAccount")}
            </p>
            <Link 
              to="/register" 
              className="text-[#d1b16a] hover:text-[#d1b16a]/80 font-semibold transition-colors"
            >
              {t("register")}
            </Link>
          </div>
        </GlassCard>
      </motion.div>
    </div>
  );
}