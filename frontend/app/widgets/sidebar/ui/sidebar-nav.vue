<script setup lang="ts">
import { useAuthStore } from '@features/auth/model/auth-store';

const authStore = useAuthStore();
const route = useRoute();
const { locale, locales, setLocale, t } = useI18n();
const localePath = useLocalePath();
const colorMode = useColorMode();

const mobileMenuOpen = ref(false);

const localeItems = computed(() =>
  locales.value.map((item) => {
    const code = String(item.code);
    return {
      label: item.name ?? code.toUpperCase(),
      value: code,
    };
  })
);

const userRoleLabel = computed(() => {
  if (authStore.user?.role === 'doctor') {
    return t('common.roles.doctor');
  }
  if (authStore.user?.role === 'patient') {
    return t('common.roles.patient');
  }
  if (authStore.user?.role === 'admin') {
    return t('common.roles.admin');
  }
  return t('common.unknown');
});

const isDark = computed(() => colorMode.value === 'dark');

const navigationItems = computed(() => {
  const items: { key: string; to: string; show: boolean }[] = [
    { key: 'nav.dashboard', to: localePath('/dashboard'), show: true },
    { key: 'nav.patients', to: localePath('/patients'), show: authStore.user?.role === 'doctor' },
    {
      key: 'nav.setupAccount',
      to: localePath('/setup-account'),
      show: Boolean(authStore.requiresAccountSetup),
    },
  ];

  return items.filter((item) => item.show);
});

function toggleTheme() {
  colorMode.preference = colorMode.value === 'dark' ? 'light' : 'dark';
}

function handleLocaleChange(value: string) {
  if (value === 'en' || value === 'ru') {
    setLocale(value);
  }
}

watch(
  () => route.fullPath,
  () => {
    mobileMenuOpen.value = false;
  }
);

onMounted(() => {
  authStore.loadFromStorage();
  if (authStore.isAuthenticated && !authStore.user) {
    authStore.fetchMe();
  }
});
</script>

<template>
  <header class="app-mobile-topbar flex lg:hidden">
    <button
      type="button"
      class="app-icon-btn"
      :aria-label="t('nav.openMenu')"
      @click="mobileMenuOpen = true"
    >
      <UIcon name="i-heroicons-bars-3" />
    </button>

    <div class="app-brand-wrap">
      <span class="app-brand-mark">D</span>
      <span class="app-brand-name">Docassist</span>
    </div>

    <button
      type="button"
      class="app-icon-btn"
      :aria-label="t('nav.themeToggle')"
      @click="toggleTheme"
    >
      <UIcon :name="isDark ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'" />
    </button>
  </header>

  <aside class="app-sidebar hidden lg:flex">
    <div class="app-brand-wrap">
      <span class="app-brand-mark">D</span>
      <span class="app-brand-name">Docassist</span>
    </div>

    <nav class="app-nav-list">
      <NuxtLink
        v-for="item in navigationItems"
        :key="item.to"
        :to="item.to"
        class="app-nav-link"
        active-class="app-nav-link-active"
      >
        {{ t(item.key) }}
      </NuxtLink>
    </nav>

    <div class="app-sidebar-footer">
      <div class="app-sidebar-control-row">
        <button
          type="button"
          class="app-icon-btn"
          :aria-label="t('nav.themeToggle')"
          @click="toggleTheme"
        >
          <UIcon :name="isDark ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'" />
        </button>

        <USelect
          :model-value="locale"
          value-key="value"
          :items="localeItems"
          size="xs"
          class="w-full"
          @update:model-value="handleLocaleChange"
        />
      </div>

      <div v-if="authStore.user" class="app-user-card">
        <p data-testid="user-email" class="app-user-email">{{ authStore.user.email }}</p>
        <UBadge size="xs" variant="subtle" color="primary">{{ userRoleLabel }}</UBadge>
      </div>

      <NuxtLink :to="localePath('/logout')" class="app-logout-btn">
        <UIcon name="i-heroicons-arrow-left-on-rectangle" />
        {{ t('common.logout') }}
      </NuxtLink>
    </div>
  </aside>

  <Transition name="drawer-fade">
    <div
      v-if="mobileMenuOpen"
      class="app-mobile-overlay lg:hidden"
      @click="mobileMenuOpen = false"
    />
  </Transition>

  <Transition name="drawer-slide">
    <aside v-if="mobileMenuOpen" class="app-mobile-drawer flex lg:hidden">
      <div class="flex items-center justify-between gap-3">
        <div class="app-brand-wrap">
          <span class="app-brand-mark">D</span>
          <span class="app-brand-name">Docassist</span>
        </div>
        <button
          type="button"
          class="app-icon-btn"
          :aria-label="t('common.close')"
          @click="mobileMenuOpen = false"
        >
          <UIcon name="i-heroicons-x-mark" />
        </button>
      </div>

      <nav class="app-nav-list mt-6">
        <NuxtLink
          v-for="item in navigationItems"
          :key="`mobile-${item.to}`"
          :to="item.to"
          class="app-nav-link"
          active-class="app-nav-link-active"
        >
          {{ t(item.key) }}
        </NuxtLink>
      </nav>

      <div class="app-sidebar-footer mt-auto">
        <div class="app-sidebar-control-row">
          <button
            type="button"
            class="app-icon-btn"
            :aria-label="t('nav.themeToggle')"
            @click="toggleTheme"
          >
            <UIcon :name="isDark ? 'i-heroicons-sun-20-solid' : 'i-heroicons-moon-20-solid'" />
          </button>

          <USelect
            :model-value="locale"
            value-key="value"
            :items="localeItems"
            size="xs"
            class="w-full"
            @update:model-value="handleLocaleChange"
          />
        </div>

        <div v-if="authStore.user" class="app-user-card">
          <p data-testid="user-email" class="app-user-email">{{ authStore.user.email }}</p>
          <UBadge size="xs" variant="subtle" color="primary">{{ userRoleLabel }}</UBadge>
        </div>

        <NuxtLink :to="localePath('/logout')" class="app-logout-btn">
          <UIcon name="i-heroicons-arrow-left-on-rectangle" />
          {{ t('common.logout') }}
        </NuxtLink>
      </div>
    </aside>
  </Transition>
</template>
