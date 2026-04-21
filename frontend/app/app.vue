<script setup lang="ts">
const { t, locale } = useI18n();

useHead(() => ({
  htmlAttrs: {
    lang: locale.value,
  },
}));

useSeoMeta({
  title: t('seo.defaultTitle'),
  ogTitle: t('seo.defaultTitle'),
  description: t('seo.defaultDescription'),
  ogDescription: t('seo.defaultDescription'),
  twitterTitle: t('seo.defaultTitle'),
  twitterDescription: t('seo.defaultDescription'),
});
</script>

<template>
  <UApp>
    <NuxtLayout>
      <NuxtRouteAnnouncer />
      <NuxtPage />
    </NuxtLayout>
  </UApp>
</template>
