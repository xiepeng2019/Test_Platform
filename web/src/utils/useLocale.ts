import { useContext } from 'react';
import { GlobalContext } from '../context';
import defaultLocale from '../locale';

function useLocale(locale = null) {
  const { lang } = useContext(GlobalContext);
  if (!locale) {
    return defaultLocale[lang] || {};
  } else {
    locale = {
      'en-US': {
        ...defaultLocale['en-US'],
        ...locale['en-US'],
      },
      'zh-CN': {
        ...defaultLocale['zh-CN'],
        ...locale['zh-CN'],
      },
    }
  }
  return (locale)[lang] || {};
}

export default useLocale;
