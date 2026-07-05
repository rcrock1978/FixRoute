<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { useWorkOrderStore } from '@/stores/workorder';

const route = useRoute();
const store = useWorkOrderStore();
const workOrderId = String(route.params.id);
const duplicates = ref<Array<{ work_order_id: string; similarity_score: number; title: string }>>([]);

onMounted(async () => {
  if (store.current?.id !== workOrderId) {
    await store.fetchTriage(workOrderId);
  } else {
    await store.fetchTriage(workOrderId);
  }
  duplicates.value = (await store.findDuplicates(workOrderId)) as typeof duplicates.value;
});
</script>

<template>
  <div class="request-status">
    <h1>Request status</h1>
    <section v-if="store.triage" class="triage">
      <h2>AI Triage</h2>
      <p><strong>Category:</strong> {{ store.triage.category }}</p>
      <p><strong>Urgency:</strong> {{ store.triage.urgency }}</p>
      <p><strong>Confidence:</strong> {{ (store.triage.confidence * 100).toFixed(1) }}%</p>
      <div v-if="store.triage.troubleshooting_steps.length">
        <h3>Try this first</h3>
        <ol>
          <li v-for="step in store.triage.troubleshooting_steps" :key="step.step">
            {{ step.description }}
          </li>
        </ol>
      </div>
    </section>
    <section v-if="duplicates.length" class="duplicates">
      <h3>Similar open requests</h3>
      <ul>
        <li v-for="dup in duplicates" :key="dup.work_order_id">
          {{ dup.title }} (similarity: {{ (dup.similarity_score * 100).toFixed(0) }}%)
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.request-status {
  max-width: 600px;
  margin: 0 auto;
  padding: 1.5rem;
}
.triage {
  background: #f3f4f6;
  padding: 1rem;
  border-radius: 8px;
}
.duplicates {
  margin-top: 1rem;
  padding: 1rem;
  border: 1px solid #fbbf24;
  border-radius: 8px;
}
</style>
