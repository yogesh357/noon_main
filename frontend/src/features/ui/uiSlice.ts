import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import type { Language } from '../../types'

interface UIState {
  language: Language
  notificationCount: number
  searchOpen: boolean
  mobileMenuOpen: boolean
  toast: { message: string; type: 'success' | 'error' | 'info' } | null
}

const initialState: UIState = {
  language: 'en',
  notificationCount: 0,
  searchOpen: false,
  mobileMenuOpen: false,
  toast: null,
}

const uiSlice = createSlice({
  name: 'ui',
  initialState,
  reducers: {
    setLanguage(state, action: PayloadAction<Language>) {
      state.language = action.payload
      localStorage.setItem('language', action.payload)
    },
    setNotificationCount(state, action: PayloadAction<number>) {
      state.notificationCount = action.payload
    },
    decrementNotificationCount(state) {
      state.notificationCount = Math.max(0, state.notificationCount - 1)
    },
    setSearchOpen(state, action: PayloadAction<boolean>) {
      state.searchOpen = action.payload
    },
    setMobileMenuOpen(state, action: PayloadAction<boolean>) {
      state.mobileMenuOpen = action.payload
    },
    showToast(state, action: PayloadAction<{ message: string; type: 'success' | 'error' | 'info' }>) {
      state.toast = action.payload
    },
    clearToast(state) {
      state.toast = null
    },
  },
})

export const {
  setLanguage, setNotificationCount,
  decrementNotificationCount, setSearchOpen, setMobileMenuOpen,
  showToast, clearToast,
} = uiSlice.actions

export default uiSlice.reducer
