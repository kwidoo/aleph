<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

interface User {
  id: string;
  name: string;
  avatar?: string;
  role: string;
  department?: string;
}

interface Props {
  user: User;
  isActive?: boolean;
  showDetails?: boolean;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  'update': [user: User];
  'view-profile': [userId: string];
}>();

const isExpanded = ref(props.showDetails || false);
const isHovered = ref(false);

const roleClasses = computed(() => {
  return {
    'bg-blue-100 text-blue-800': props.user.role === 'Admin',
    'bg-green-100 text-green-800': props.user.role === 'Editor',
    'bg-purple-100 text-purple-800': props.user.role === 'Author',
    'bg-gray-100 text-gray-800': !['Admin', 'Editor', 'Author'].includes(props.user.role)
  };
});

const avatarUrl = computed(() => {
  return props.user.avatar || `https://ui-avatars.com/api/?name=${encodeURIComponent(props.user.name)}&background=random`;
});

const toggleDetails = () => {
  isExpanded.value = !isExpanded.value;
};

const viewProfile = () => {
  emit('view-profile', props.user.id);
};

onMounted(() => {
  // Any initialization logic
});
</script>

<template>
  <div
    class="user-card bg-white rounded-lg shadow-md p-4 transition-all duration-200"
    :class="{ 'border-blue-500 border-2': isActive, 'hover:shadow-lg': !isHovered }"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    aria-label="User Card"
  >
    <div class="flex items-center">
      <img
        :src="avatarUrl"
        :alt="`${user.name}'s avatar`"
        class="w-12 h-12 rounded-full object-cover"
      />

      <div class="ml-4 flex-grow">
        <h3 class="text-lg font-medium text-gray-900">{{ user.name }}</h3>

        <span
          class="px-2 py-1 text-xs rounded-full inline-flex items-center"
          :class="roleClasses"
        >
          {{ user.role }}
        </span>
      </div>

      <button
        type="button"
        class="text-gray-400 hover:text-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        @click="toggleDetails"
        :aria-expanded="isExpanded"
        aria-controls="user-details"
      >
        <span class="sr-only">{{ isExpanded ? 'Hide details' : 'Show details' }}</span>
        <svg class="h-5 w-5" :class="{ 'transform rotate-180': isExpanded }" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <div
      v-if="isExpanded"
      id="user-details"
      class="mt-4 border-t pt-3"
    >
      <div v-if="user.department" class="flex items-center mb-2">
        <span class="text-gray-500 text-sm">Department:</span>
        <span class="ml-2 text-gray-900">{{ user.department }}</span>
      </div>

      <button
        type="button"
        class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
        @click="viewProfile"
      >
        View Profile
      </button>
    </div>
  </div>
</template>

<style scoped>
.user-card {
  max-width: 400px;
}
</style>
