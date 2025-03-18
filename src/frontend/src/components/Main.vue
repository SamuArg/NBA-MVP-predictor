<template>
    <div>
        <PredictionTable @update-date="updateDate"/>
        <PlayerLine :date="date"/>
    </div>
</template>

<script>
import MvpChart from './MvpChart.vue';
import PlayerLine from './PlayerLine.vue';

export default {
    components: {
        PredictionTable: MvpChart,
        PlayerLine
    },
    data() {
        return {
            date: null
        }
    },
    methods: {
        updateDate(date) {
            this.date = date;
        }
    }
}
</script>
