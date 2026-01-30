import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { Globe, ChevronDown, Search, Check } from 'lucide-react';
import { SUPPORTED_LANGUAGES } from '../i18n/index';

export default function LanguageSelector({ variant = 'default' }) {
  const { i18n, t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState('');

  const currentLang = SUPPORTED_LANGUAGES.find(l => l.code === i18n.language) || SUPPORTED_LANGUAGES[0];

  const filteredLanguages = SUPPORTED_LANGUAGES.filter(lang =>
    lang.name.toLowerCase().includes(search.toLowerCase()) ||
    lang.native.toLowerCase().includes(search.toLowerCase())
  );

  const changeLanguage = (code) => {
    i18n.changeLanguage(code);
    setIsOpen(false);
    setSearch('');
  };

  // Popular languages for quick access
  const popularLangs = ['en', 'es', 'zh', 'hi', 'ar', 'pt', 'fr', 'de', 'ja', 'ko'];
  const popularLanguages = SUPPORTED_LANGUAGES.filter(l => popularLangs.includes(l.code));

  if (variant === 'compact') {
    return (
      <div className="relative">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <Globe className="w-4 h-4" />
          <span className="text-sm">{currentLang.flag} {currentLang.code.toUpperCase()}</span>
          <ChevronDown className="w-3 h-3" />
        </button>

        {isOpen && (
          <>
            <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
            <div className="absolute right-0 top-full mt-2 w-72 bg-white dark:bg-slate-900 rounded-xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50 overflow-hidden">
              {/* Search */}
              <div className="p-3 border-b border-slate-200 dark:border-slate-700">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                  <input
                    type="text"
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    placeholder="Search language..."
                    className="w-full pl-10 pr-4 py-2 bg-slate-100 dark:bg-slate-800 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                  />
                </div>
              </div>

              {/* Quick access */}
              {!search && (
                <div className="p-3 border-b border-slate-200 dark:border-slate-700">
                  <p className="text-xs text-slate-500 mb-2">Popular</p>
                  <div className="flex flex-wrap gap-1">
                    {popularLanguages.map(lang => (
                      <button
                        key={lang.code}
                        onClick={() => changeLanguage(lang.code)}
                        className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                          currentLang.code === lang.code
                            ? 'bg-violet-500 text-white'
                            : 'bg-slate-100 dark:bg-slate-800 hover:bg-violet-100 dark:hover:bg-violet-900/30'
                        }`}
                      >
                        {lang.flag} {lang.code.toUpperCase()}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* All languages */}
              <div className="max-h-64 overflow-y-auto">
                {filteredLanguages.map(lang => (
                  <button
                    key={lang.code}
                    onClick={() => changeLanguage(lang.code)}
                    className={`w-full flex items-center justify-between px-4 py-2.5 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors ${
                      currentLang.code === lang.code ? 'bg-violet-50 dark:bg-violet-900/20' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-lg">{lang.flag}</span>
                      <div className="text-left">
                        <p className="text-sm font-medium">{lang.name}</p>
                        <p className="text-xs text-slate-500">{lang.native}</p>
                      </div>
                    </div>
                    {currentLang.code === lang.code && (
                      <Check className="w-4 h-4 text-violet-500" />
                    )}
                  </button>
                ))}
              </div>

              <div className="p-2 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800/50">
                <p className="text-xs text-center text-slate-500">
                  80 languages supported
                </p>
              </div>
            </div>
          </>
        )}
      </div>
    );
  }

  // Default full variant
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 hover:border-violet-500 transition-colors"
      >
        <span className="text-xl">{currentLang.flag}</span>
        <div className="text-left">
          <p className="text-sm font-medium">{currentLang.name}</p>
          <p className="text-xs text-slate-500">{currentLang.native}</p>
        </div>
        <ChevronDown className="w-4 h-4 ml-2 text-slate-400" />
      </button>

      {isOpen && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
          <div className="absolute left-0 top-full mt-2 w-80 bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 z-50 overflow-hidden">
            {/* Search */}
            <div className="p-4 border-b border-slate-200 dark:border-slate-700">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                <input
                  type="text"
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  placeholder="Search 80 languages..."
                  className="w-full pl-10 pr-4 py-2.5 bg-slate-100 dark:bg-slate-800 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-violet-500"
                  autoFocus
                />
              </div>
            </div>

            {/* Popular */}
            {!search && (
              <div className="p-4 border-b border-slate-200 dark:border-slate-700">
                <p className="text-xs font-semibold text-slate-500 uppercase mb-3">Popular Languages</p>
                <div className="grid grid-cols-2 gap-2">
                  {popularLanguages.map(lang => (
                    <button
                      key={lang.code}
                      onClick={() => changeLanguage(lang.code)}
                      className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-all ${
                        currentLang.code === lang.code
                          ? 'bg-violet-500 text-white'
                          : 'bg-slate-100 dark:bg-slate-800 hover:bg-violet-100 dark:hover:bg-violet-900/30'
                      }`}
                    >
                      <span>{lang.flag}</span>
                      <span className="font-medium">{lang.name}</span>
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* All */}
            <div className="max-h-72 overflow-y-auto">
              <p className="px-4 pt-3 pb-2 text-xs font-semibold text-slate-500 uppercase sticky top-0 bg-white dark:bg-slate-900">
                {search ? `Results (${filteredLanguages.length})` : 'All Languages'}
              </p>
              {filteredLanguages.map(lang => (
                <button
                  key={lang.code}
                  onClick={() => changeLanguage(lang.code)}
                  className={`w-full flex items-center justify-between px-4 py-3 hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors ${
                    currentLang.code === lang.code ? 'bg-violet-50 dark:bg-violet-900/20' : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{lang.flag}</span>
                    <div className="text-left">
                      <p className="font-medium">{lang.name}</p>
                      <p className="text-sm text-slate-500">{lang.native}</p>
                    </div>
                  </div>
                  {currentLang.code === lang.code && (
                    <Check className="w-5 h-5 text-violet-500" />
                  )}
                </button>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
