<template>
  <router-view @route-change="resetBackground" />
</template>

<script>
export default {
  methods: {
    resetBackground() {
      document.body.style.background = "none"; // Resets the background
    }
  }
};
</script>
