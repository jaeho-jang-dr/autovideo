// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
// 다국어: 기본 로캘(ko)은 접두사 없이('/'), 영어는 '/en' 접두사로 라우팅된다.
export default defineConfig({
  site: 'https://drjayed.com',
  i18n: {
    defaultLocale: 'ko',
    locales: ['ko', 'en'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
