<script setup lang="ts">
import { RouterView } from 'vue-router';
</script>

<template>
  <div id="app">
    <header>
      <h1>FixRoute</h1>
      <nav>
        <RouterLink to="/">Submit request</RouterLink>
      </nav>
    </header>
    <main>
      <RouterView />
    </main>
  </div>
</template>

<style>
:root {
  font-family: system-ui, sans-serif;
  color: #1f2937;
}
body {
  margin: 0;
  background: #f9fafb;
}
header {
  background: #1e3a8a;
  color: white;
  padding: 1rem 1.5rem;
  display: flex;
  align-items: center;
  gap: 2rem;
}
header h1 {
  margin: 0;
  font-size: 1.5rem;
}
header a {
  color: white;
  text-decoration: none;
}
main {
  padding: 1.5rem;
}
</style>
