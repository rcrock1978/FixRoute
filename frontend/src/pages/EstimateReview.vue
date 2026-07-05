<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';
import { API_BASE_URL } from '@/services/api';
import { useTenantStore } from '@/stores/tenant';

const route = useRoute();
const tenant = useTenantStore();
const dispatchId = String(route.params.id);

const lineItems = ref([{ description: '', amount: 0 }]);
const comment = ref('');
const review = ref<'approve' | 'reject' | 'request_revision' | ''>('');

onMounted(() => {
  // No-op; PM enters estimate review from list page
});

function addLineItem(): void {
  lineItems.value.push({ description: '', amount: 0 });
}

function totalAmount(): number {
  return lineItems.value.reduce((s, li) => s + Number(li.amount || 0), 0);
}

async function submit(): Promise<void> {
  await axios.post(
    `${API_BASE_URL}/dispatches/${dispatchId}/estimate/`,
    { line_items: lineItems.value, total: totalAmount() },
    { headers: { 'X-Tenant-ID': tenant.id ?? '' } },
  );
}
</script>

<template>
  <div class="estimate-review">
    <h1>Estimate for dispatch {{ dispatchId }}</h1>
    <table>
      <thead>
        <tr><th>Description</th><th>Amount ($)</th></tr>
      </thead>
      <tbody>
        <tr v-for="(item, idx) in lineItems" :key="idx">
          <td><input v-model="item.description" /></td>
          <td><input v-model.number="item.amount" type="number" step="0.01" /></td>
        </tr>
      </tbody>
      <tfoot>
        <tr><td>Total</td><td>${{ totalAmount().toFixed(2) }}</td></tr>
      </tfoot>
    </table>
    <button type="button" @click="addLineItem">+ Add line item</button>
    <button type="button" @click="submit">Submit estimate</button>
  </div>
</template>

<style scoped>
.estimate-review {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem;
}
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 1rem;
}
th, td {
  padding: 0.5rem;
  border-bottom: 1px solid #e5e7eb;
  text-align: left;
}
button {
  margin-right: 0.5rem;
  padding: 0.5rem 1rem;
  background: #2563eb;
  color: white;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
}
</style>
