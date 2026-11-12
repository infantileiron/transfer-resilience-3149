<script setup lang="ts">defineProps<{code:string;title:string;description:string}>();
</script><template><header class="page-heading"><div><span class="eyebrow">{{code}}</span><h1>{{title}}</h1></div><p>{{description}}</p></header></template>
