<script setup lang="ts">
// Layout is composed from the SidebarNav widget
</script>

<template>
  <div
    class="min-h-screen flex bg-[radial-gradient(circle_at_top,_#f8fafc,_#eef2ff_45%,_#e2e8f0)] text-slate-900"
  >
    <SidebarNav />
    <main class="flex-1 overflow-auto p-6 md:p-8">
      <slot />
    </main>
  </div>
</template>
