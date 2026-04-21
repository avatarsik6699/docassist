// https://nuxt.com/docs/api/configuration/nuxt-config
import { fileURLToPath } from 'node:url';

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },

  future: {
    compatibilityVersion: 4,
  },

  modules: ['@nuxt/ui', '@nuxtjs/i18n', '@pinia/nuxt'],
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      htmlAttrs: {
        lang: 'en',
      },
      titleTemplate: '%s · Docassist',
      title: 'Clinical dashboard',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        {
          name: 'description',
          content:
            'Docassist helps clinicians and patients track medications, adherence, questionnaires, and safety signals in one secure dashboard.',
        },
        { name: 'format-detection', content: 'telephone=no' },
        { name: 'robots', content: 'index,follow,max-image-preview:large' },
        { property: 'og:type', content: 'website' },
        { property: 'og:site_name', content: 'Docassist' },
        { property: 'og:title', content: 'Docassist' },
        {
          property: 'og:description',
          content:
            'Clinical monitoring workspace for medication plans, adherence logs, and patient-reported outcomes.',
        },
        { property: 'og:image', content: '/android-chrome-512x512.png' },
        { property: 'og:locale', content: 'en_US' },
        { name: 'twitter:card', content: 'summary_large_image' },
        { name: 'twitter:title', content: 'Docassist' },
        {
          name: 'twitter:description',
          content:
            'Clinical monitoring workspace for medication plans, adherence logs, and patient-reported outcomes.',
        },
        { name: 'twitter:image', content: '/android-chrome-512x512.png' },
        { name: 'theme-color', content: '#0b2236' },
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'icon', type: 'image/png', sizes: '16x16', href: '/favicon-16x16.png' },
        { rel: 'icon', type: 'image/png', sizes: '32x32', href: '/favicon-32x32.png' },
        { rel: 'apple-touch-icon', sizes: '180x180', href: '/apple-touch-icon.png' },
        { rel: 'manifest', href: '/site.webmanifest' },
      ],
    },
  },

  // FSD layer path aliases
  alias: {
    '@shared': fileURLToPath(new URL('./app/shared', import.meta.url)),
    '@features': fileURLToPath(new URL('./app/features', import.meta.url)),
    '@widgets': fileURLToPath(new URL('./app/widgets', import.meta.url)),
  },

  // Auto-import composables/stores from FSD directories (paths relative to srcDir)
  imports: {
    dirs: ['shared/api', 'shared/lib', 'shared/model', 'features/auth/model'],
  },

  // Auto-import components from FSD widget layer
  components: [{ path: '~/widgets', pathPrefix: false }],

  i18n: {
    locales: [
      { code: 'en', language: 'en-US', file: 'en.json', name: 'English' },
      { code: 'ru', language: 'ru-RU', file: 'ru.json', name: 'Русский' },
    ],
    defaultLocale: 'en',
    strategy: 'prefix_except_default',
    langDir: 'locales',
    detectBrowserLanguage: {
      useCookie: true,
      cookieKey: 'i18n_redirected',
      redirectOn: 'root',
    },
  },

  colorMode: {
    preference: 'system',
    fallback: 'light',
    classSuffix: '',
  },

  runtimeConfig: {
    apiBaseInternal:
      process.env.NUXT_API_BASE_INTERNAL ??
      process.env.API_BASE_INTERNAL_URL ??
      process.env.API_BASE_URL ??
      'http://localhost:8000/api/v1',
    public: {
      apiBase: process.env.API_BASE_URL ?? 'http://localhost:8000/api/v1',
    },
  },
});
