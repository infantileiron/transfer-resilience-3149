<script setup lang="ts">defineProps<{error?:boolean}>();
</script><template><div :class="['notice',{error}]" :role="error?'alert':undefined"><slot/></div></template>
