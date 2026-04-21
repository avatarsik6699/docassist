<script setup lang="ts">
const authStore = useAuthStore();
const localePath = useLocalePath();

await navigateTo(localePath(authStore.isAuthenticated ? '/dashboard' : '/login'));
</script>
