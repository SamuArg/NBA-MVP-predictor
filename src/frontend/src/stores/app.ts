// Utilities
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    selectedDate: '',
    loading: true,
  }),
  actions: {
    setSelectedDate(date: string) {
      this.selectedDate = date;
    },
    setLoading(state: boolean){
      this.loading = state;
    }
  },
})
