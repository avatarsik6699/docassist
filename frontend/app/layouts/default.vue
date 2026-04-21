<script setup lang="ts">
// Layout is composed from the SidebarNav widget
</script>

<template>
  <div class="app-shell">
    <SidebarNav />
    <main class="app-main">
      <slot />
    </main>
  </div>
</template>
