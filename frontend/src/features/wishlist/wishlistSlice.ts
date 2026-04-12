import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'
import { wishlistService } from '../../services/api.service'
import type { Product } from '../../types'

interface WishlistState {
  productIds: number[]
  products: Product[]
  loading: boolean
}

const initialState: WishlistState = {
  productIds: [],
  products: [],
  loading: false,
}

export const fetchWishlist = createAsyncThunk('wishlist/fetch', async (_, { rejectWithValue }) => {
  try {
    const { data } = await wishlistService.getWishlist()
    return data
  } catch {
    return rejectWithValue('Failed to load wishlist')
  }
})

export const toggleWishlist = createAsyncThunk(
  'wishlist/toggle',
  async (productId: number, { rejectWithValue }) => {
    try {
      const { data } = await wishlistService.toggle(productId)
      return { productId, isWishlisted: data.is_wishlisted }
    } catch {
      return rejectWithValue('Failed to update wishlist')
    }
  },
)

const wishlistSlice = createSlice({
  name: 'wishlist',
  initialState,
  reducers: {},
  extraReducers: (builder) => {
    builder
      .addCase(fetchWishlist.pending, (state) => { state.loading = true })
      .addCase(fetchWishlist.fulfilled, (state, action) => {
        state.loading = false
        state.productIds = action.payload.product_ids
        state.products = action.payload.products
      })
      .addCase(fetchWishlist.rejected, (state) => { state.loading = false })
      .addCase(toggleWishlist.fulfilled, (state, action) => {
        const { productId, isWishlisted } = action.payload
        if (isWishlisted) {
          if (!state.productIds.includes(productId)) {
            state.productIds.push(productId)
          }
        } else {
          state.productIds = state.productIds.filter((id) => id !== productId)
          state.products = state.products.filter((p) => p.id !== productId)
        }
      })
  },
})

export default wishlistSlice.reducer
