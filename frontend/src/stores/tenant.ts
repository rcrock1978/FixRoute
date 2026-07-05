import { defineStore } from 'pinia';
import { ref } from 'vue';

export const useTenantStore = defineStore('tenant', () => {
  const id = ref<string | null>(localStorage.getItem('tenant_id'));
  const role = ref<string | null>(localStorage.getItem('user_role'));

  function setTenant(tenantId: string, userRole: string): void {
    id.value = tenantId;
    role.value = userRole;
    localStorage.setItem('tenant_id', tenantId);
    localStorage.setItem('user_role', userRole);
  }

  return { id, role, setTenant };
});
