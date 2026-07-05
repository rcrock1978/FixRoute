import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router';
import RequestSubmit from '@/pages/RequestSubmit.vue';
import RequestStatus from '@/pages/RequestStatus.vue';
import DispatchWorkflow from '@/pages/DispatchWorkflow.vue';
import EstimateReview from '@/pages/EstimateReview.vue';
import AnalyticsDashboard from '@/pages/AnalyticsDashboard.vue';

const routes: RouteRecordRaw[] = [
  { path: '/', name: 'submit', component: RequestSubmit },
  { path: '/requests/:id', name: 'status', component: RequestStatus },
  { path: '/dispatch/:id', name: 'dispatch', component: DispatchWorkflow },
  { path: '/estimates/:id', name: 'estimate', component: EstimateReview },
  { path: '/analytics', name: 'analytics', component: AnalyticsDashboard },
];

export const router = createRouter({
  history: createWebHistory(),
  routes,
});
