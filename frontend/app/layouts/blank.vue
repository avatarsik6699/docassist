<template>
  <div class="auth-layout min-h-screen flex items-center justify-center px-4 py-10">
    <div class="absolute inset-0 pointer-events-none">
      <div class="hero-orb hero-orb-left" />
      <div class="hero-orb hero-orb-right" />
    </div>
    <div class="relative w-full flex items-center justify-center">
      <slot />
    </div>
  </div>
</template>
