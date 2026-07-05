import { defineStore } from 'pinia';
import { ref } from 'vue';
import { api } from '@/services/api';

export interface WorkOrder {
  id: string;
  property: string;
  submitted_by: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  category: string | null;
  media_attachments: Array<{ blob_url: string; type: string; filename: string }>;
  voice_transcript: string;
  created_at: string;
  updated_at: string;
}

export interface TriageResult {
  work_order_id: string;
  category: string;
  urgency: string;
  confidence: number;
  troubleshooting_steps: Array<{ step: number; description: string }>;
  ai_model_version: string;
  classification_time_ms: number;
}

export const useWorkOrderStore = defineStore('workorder', () => {
  const workOrders = ref<WorkOrder[]>([]);
  const current = ref<WorkOrder | null>(null);
  const triage = ref<TriageResult | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function submit(payload: {
    property_id: string;
    title: string;
    description: string;
    media?: File[];
    voice_recording?: File;
  }): Promise<WorkOrder> {
    loading.value = true;
    error.value = null;
    try {
      const formData = new FormData();
      formData.append('property_id', payload.property_id);
      formData.append('title', payload.title);
      formData.append('description', payload.description);
      if (payload.media) {
        for (const file of payload.media) formData.append('media', file);
      }
      if (payload.voice_recording) formData.append('voice_recording', payload.voice_recording);
      const { data } = await api.post<WorkOrder>('/work-orders/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      current.value = data;
      return data;
    } catch (e) {
      const err = e as { response?: { data?: { detail?: string } } };
      error.value = err.response?.data?.detail ?? 'Submission failed';
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTriage(workOrderId: string): Promise<TriageResult | null> {
    try {
      const { data } = await api.get<TriageResult>(`/work-orders/${workOrderId}/triage/`);
      triage.value = data;
      return data;
    } catch {
      triage.value = null;
      return null;
    }
  }

  async function findDuplicates(workOrderId: string): Promise<unknown[]> {
    const { data } = await api.get<{ matches: unknown[] }>(`/work-orders/${workOrderId}/duplicates/`);
    return data.matches;
  }

  return { workOrders, current, triage, loading, error, submit, fetchTriage, findDuplicates };
});
