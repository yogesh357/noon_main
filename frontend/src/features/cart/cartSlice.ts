import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import type { Cart } from '../../types'
import { cartService } from '../../services/api.service'

interface CartState {
  cart: Cart | null
  count: number
  loading: boolean
  error: string | null
}

const initialState: CartState = {
  cart: null,
  count: 0,
  loading: false,
  error: null,
}

// ─── Thunks ───────────────────────────────────────────────────────────────────

export const fetchCart = createAsyncThunk('cart/fetchCart', async (_, { rejectWithValue }) => {
  try {
    const { data } = await cartService.getCart()
    return data
  } catch {
    return rejectWithValue('Failed to load cart')
  }
})

export const fetchCartCount = createAsyncThunk('cart/fetchCount', async (_, { rejectWithValue }) => {
  try {
    const { data } = await cartService.getCount()
    return data.count
  } catch {
    return rejectWithValue('Failed to load cart count')
  }
})

export const addToCart = createAsyncThunk(
  'cart/addItem',
  async ({ variantId, quantity }: { variantId: number; quantity: number }, { dispatch, rejectWithValue }) => {
    try {
      await cartService.addItem(variantId, quantity)
      dispatch(fetchCart())
      return true
    } catch (err: unknown) {
      const error = err as { response?: { data?: { detail?: string } } }
      return rejectWithValue(error.response?.data?.detail ?? 'Failed to add item')
    }
  },
)

export const updateCartItem = createAsyncThunk(
  'cart/updateItem',
  async ({ itemId, quantity }: { itemId: number; quantity: number }, { dispatch, rejectWithValue }) => {
    try {
      await cartService.updateItem(itemId, quantity)
      dispatch(fetchCart())
      return true
    } catch {
      return rejectWithValue('Failed to update item')
    }
  },
)

export const removeFromCart = createAsyncThunk(
  'cart/removeItem',
  async (itemId: number, { dispatch, rejectWithValue }) => {
    try {
      await cartService.removeItem(itemId)
      dispatch(fetchCart())
      return true
    } catch {
      return rejectWithValue('Failed to remove item')
    }
  },
)

// ─── Slice ────────────────────────────────────────────────────────────────────

const cartSlice = createSlice({
  name: 'cart',
  initialState,
  reducers: {
    clearCart(state) {
      state.cart = null
      state.count = 0
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCart.pending, (state) => { state.loading = true })
      .addCase(fetchCart.fulfilled, (state, action) => {
        state.loading = false
        state.cart = action.payload
        state.count = action.payload.total_items
      })
      .addCase(fetchCart.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      .addCase(fetchCartCount.fulfilled, (state, action) => {
        state.count = action.payload
      })
  },
})

export const { clearCart } = cartSlice.actions
export default cartSlice.reducer
