// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
// 다국어: 기본 로캘(en)은 접두사 없이('/'), 한국어는 '/ko' 접두사로 라우팅된다.
export default defineConfig({
  site: 'https://drjayed.com',
  // 원격(아이폰 등)에서 볼 수 있도록 LAN 바인딩 + 터널 호스트 허용
  server: { host: true, allowedHosts: true },
  vite: { server: { allowedHosts: true, host: true } },
  i18n: {
    defaultLocale: 'en',
    locales: ['ko', 'en'],
    routing: {
      prefixDefaultLocale: false,
    },
  },
});
