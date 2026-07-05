<script setup lang="ts">
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { API_BASE_URL } from '@/services/api';
import { useTenantStore } from '@/stores/tenant';

const tenant = useTenantStore();
const start = ref(new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10));
const end = ref(new Date().toISOString().slice(0, 10));
const groupBy = ref<'trade' | 'vendor' | 'property' | 'month'>('trade');
const data = ref<{ rows: Array<Record<string, unknown>> } | null>(null);
const error = ref<string | null>(null);

async function load(): Promise<void> {
  try {
    const { data: response } = await axios.get(`${API_BASE_URL}/analytics/spend/`, {
      params: { start_date: start.value, end_date: end.value, group_by: groupBy.value },
      headers: { 'X-Tenant-ID': tenant.id ?? '' },
    });
    data.value = response;
  } catch (e) {
    error.value = (e as Error).message;
  }
}

onMounted(load);
</script>

<template>
  <div class="analytics-dashboard">
    <h1>Spend analytics</h1>
    <form @submit.prevent="load">
      <label>Start <input v-model="start" type="date" /></label>
      <label>End <input v-model="end" type="date" /></label>
      <label>Group by
        <select v-model="groupBy">
          <option value="trade">Trade</option>
          <option value="vendor">Vendor</option>
          <option value="property">Property</option>
          <option value="month">Month</option>
        </select>
      </label>
      <button type="submit">Run</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
    <table v-if="data">
      <thead>
        <tr><th>{{ groupBy }}</th><th>Total ($)</th><th>Count</th></tr>
      </thead>
      <tbody>
        <tr v-for="row in data.rows" :key="String(Object.values(row)[0])">
          <td>{{ Object.values(row)[0] }}</td>
          <td>{{ Number(Object.values(row)[1] || 0).toFixed(2) }}</td>
          <td>{{ Object.values(row)[2] }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<style scoped>
.analytics-dashboard {
  max-width: 960px;
  margin: 0 auto;
  padding: 1.5rem;
}
form {
  display: flex;
  gap: 1rem;
  margin-bottom: 1rem;
  align-items: end;
}
table {
  width: 100%;
  border-collapse: collapse;
}
th, td {
  padding: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}
.error {
  color: #dc2626;
}
</style>
