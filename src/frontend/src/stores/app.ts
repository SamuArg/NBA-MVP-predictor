// Utilities
import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    selectedDate: '',
  }),
  actions: {
    setSelectedDate(date: string) {
      this.selectedDate = date;
    },
  },
})
