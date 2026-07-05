<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { useWorkOrderStore } from '@/stores/workorder';

const store = useWorkOrderStore();
const router = useRouter();

const propertyId = ref('');
const title = ref('');
const description = ref('');
const mediaFiles = ref<File[]>([]);
const voiceRecording = ref<File | null>(null);
const recording = ref(false);
const mediaRecorder = ref<MediaRecorder | null>(null);

onMounted(() => {
  if (mediaRecorder.value) return;
});

function onMediaChange(event: Event): void {
  const input = event.target as HTMLInputElement;
  mediaFiles.value = input.files ? Array.from(input.files) : [];
}

async function startRecording(): Promise<void> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder.value = new MediaRecorder(stream);
  const chunks: Blob[] = [];
  mediaRecorder.value.ondataavailable = (e) => chunks.push(e.data);
  mediaRecorder.value.onstop = () => {
    voiceRecording.value = new File(chunks, 'voice.webm', { type: 'audio/webm' });
  };
  mediaRecorder.value.start();
  recording.value = true;
}

function stopRecording(): void {
  mediaRecorder.value?.stop();
  recording.value = false;
}

async function submit(): Promise<void> {
  const workOrder = await store.submit({
    property_id: propertyId.value,
    title: title.value,
    description: description.value,
    media: mediaFiles.value,
    voice_recording: voiceRecording.value ?? undefined,
  });
  await router.push(`/requests/${workOrder.id}`);
}
</script>

<template>
  <div class="request-submit">
    <h1>Submit a maintenance request</h1>
    <form @submit.prevent="submit">
      <label>
        Property ID
        <input v-model="propertyId" required type="text" placeholder="UUID" />
      </label>
      <label>
        Title
        <input v-model="title" required maxlength="200" type="text" />
      </label>
      <label>
        Description
        <textarea v-model="description" required rows="4"></textarea>
      </label>
      <label>
        Photos (up to 5)
        <input accept="image/*" multiple type="file" @change="onMediaChange" />
      </label>
      <div class="voice">
        <button v-if="!recording" type="button" @click="startRecording">Start voice recording</button>
        <button v-else type="button" @click="stopRecording">Stop recording</button>
        <span v-if="voiceRecording">Voice attached: {{ voiceRecording.name }}</span>
      </div>
      <button :disabled="store.loading" type="submit">
        {{ store.loading ? 'Submitting…' : 'Submit request' }}
      </button>
      <p v-if="store.error" class="error">{{ store.error }}</p>
    </form>
  </div>
</template>

<style scoped>
.request-submit {
  max-width: 600px;
  margin: 0 auto;
  padding: 1.5rem;
}
form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
label {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
input,
textarea {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button[type='submit'] {
  padding: 0.75rem;
  background: #2563eb;
  color: white;
  border: 0;
  border-radius: 4px;
  cursor: pointer;
}
.error {
  color: #dc2626;
}
</style>
