<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import { useTenantStore } from '@/stores/tenant';
import { API_BASE_URL } from '@/services/api';

const route = useRoute();
const router = useRouter();
const tenant = useTenantStore();

interface VendorMatch {
  vendor_id: string;
  name: string;
  score: number;
  eta_minutes: number;
  estimated_cost: number;
  rating: number;
  insurance_verified: boolean;
  breakdown: Record<string, number>;
}

const matches = ref<VendorMatch[]>([]);
const selected = ref<string | null>(null);
const approvalToken = ref(crypto.randomUUID());
const loading = ref(false);
const error = ref<string | null>(null);

async function loadMatches(): Promise<void> {
  loading.value = true;
  try {
    const { data } = await axios.get(
      `${API_BASE_URL}/work-orders/${route.params.id}/match-vendors/`,
      { headers: { 'X-Tenant-ID': tenant.id ?? '' } },
    );
    matches.value = data.matches;
  } catch (e) {
    error.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
}

async function confirmDispatch(): Promise<void> {
  if (!selected.value) return;
  try {
    await axios.post(
      `${API_BASE_URL}/work-orders/${route.params.id}/dispatch/`,
      { vendor_id: selected.value, approval_token: approvalToken.value },
      { headers: { 'X-Tenant-ID': tenant.id ?? '' } },
    );
    await router.push('/');
  } catch (e) {
    error.value = (e as Error).message;
  }
}

onMounted(loadMatches);
</script>

<template>
  <div class="dispatch-workflow">
    <h1>Select a vendor</h1>
    <p v-if="loading">Loading vendors…</p>
    <p v-if="error" class="error">{{ error }}</p>
    <ul v-if="matches.length">
      <li
        v-for="vendor in matches"
        :key="vendor.vendor_id"
        :class="{ selected: selected === vendor.vendor_id }"
        @click="selected = vendor.vendor_id"
      >
        <h3>{{ vendor.name }}</h3>
        <p>Score: {{ (vendor.score * 100).toFixed(0) }}%</p>
        <p>ETA: {{ vendor.eta_minutes }} min</p>
        <p>Rate: ${{ vendor.estimated_cost }}/hr</p>
        <p>Rating: {{ vendor.rating.toFixed(1) }}/5</p>
        <p v-if="vendor.insurance_verified" class="badge">✓ Insured</p>
      </li>
    </ul>
    <button v-if="selected" :disabled="loading" @click="confirmDispatch">
      Confirm dispatch
    </button>
  </div>
</template>

<style scoped>
.dispatch-workflow {
  max-width: 800px;
  margin: 0 auto;
  padding: 1.5rem;
}
ul {
  list-style: none;
  padding: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1rem;
}
li {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: border-color 0.2s;
}
li.selected {
  border-color: #2563eb;
  background: #eff6ff;
}
button {
  margin-top: 1rem;
  padding: 0.75rem 1.5rem;
  background: #2563eb;
  color: white;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
}
.badge {
  color: #059669;
  font-size: 0.875rem;
}
</style>
