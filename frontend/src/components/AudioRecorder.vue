<script setup lang="ts">
import { ref } from 'vue';

const recording = ref(false);
const audioUrl = ref<string | null>(null);

async function start(): Promise<void> {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  const recorder = new MediaRecorder(stream);
  const chunks: Blob[] = [];
  recorder.ondataavailable = (e) => chunks.push(e.data);
  recorder.onstop = () => {
    const blob = new Blob(chunks, { type: 'audio/webm' });
    audioUrl.value = URL.createObjectURL(blob);
  };
  recorder.start();
  recording.value = true;
  setTimeout(() => {
    recorder.stop();
    recording.value = false;
  }, 30_000);
}
</script>

<template>
  <div>
    <button v-if="!recording" type="button" @click="start">Record voice (max 30s)</button>
    <span v-else>Recording…</span>
    <audio v-if="audioUrl" :src="audioUrl" controls></audio>
  </div>
</template>
