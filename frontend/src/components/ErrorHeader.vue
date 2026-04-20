<script setup lang="ts">
interface Props {
  statusCode?: string | number
  title?: string
  description?: string
}

const props = withDefaults(defineProps<Props>(), {
  statusCode: '404',
  title: 'Page Not Found',
  description: 'The page you are looking for does not exist.',
})
</script>

<template>
  <div class="text-center">
    <h1 class="error-title mb-4">
      {{ props.statusCode }}
    </h1>

    <h4 class="text-h4 mb-2">
      {{ props.title }}
    </h4>

    <p class="text-body-1 text-medium-emphasis mb-0">
      {{ props.description }}
    </p>
  </div>
</template>

<style scoped>
.error-title {
  font-size: clamp(4rem, 10vw, 7rem);
  line-height: 1;
}
</style>
