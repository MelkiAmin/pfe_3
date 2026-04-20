<template>
  <Transition name="expand-transition">
    <slot />
  </Transition>
</template>

<style scoped>
.expand-transition-enter-active,
.expand-transition-leave-active {
  transition: all 0.2s ease;
}

.expand-transition-enter-from,
.expand-transition-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
