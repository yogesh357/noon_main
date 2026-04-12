import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit'
import type { Product, Category, ProductFilters, AvailableFilters } from '../../types'
import { catalogService } from '../../services/api.service'

interface CatalogState {
  products: Product[]
  categories: Category[]
  total: number
  page: number
  pages: number
  per_page: number
  filters: ProductFilters
  availableFilters: AvailableFilters | null
  loading: boolean
  error: string | null
}

const initialState: CatalogState = {
  products: [],
  categories: [],
  total: 0,
  page: 1,
  pages: 1,
  per_page: 20,
  filters: { sort: 'newest', page: 1, per_page: 20 },
  availableFilters: null,
  loading: false,
  error: null,
}

// ─── Thunks ───────────────────────────────────────────────────────────────────

export const fetchProducts = createAsyncThunk(
  'catalog/fetchProducts',
  async (filters: ProductFilters, { rejectWithValue }) => {
    try {
      const { data } = await catalogService.getProducts(filters)
      return data
    } catch {
      return rejectWithValue('Failed to load products')
    }
  },
)

export const fetchCategories = createAsyncThunk(
  'catalog/fetchCategories',
  async (_, { rejectWithValue }) => {
    try {
      const { data } = await catalogService.getCategories()
      return data
    } catch {
      return rejectWithValue('Failed to load categories')
    }
  },
)

// ─── Slice ────────────────────────────────────────────────────────────────────

const catalogSlice = createSlice({
  name: 'catalog',
  initialState,
  reducers: {
    setFilters(state, action: PayloadAction<Partial<ProductFilters>>) {
      state.filters = { ...state.filters, ...action.payload, page: 1 }
    },
    setPage(state, action: PayloadAction<number>) {
      state.filters = { ...state.filters, page: action.payload }
    },
    clearFilters(state) {
      state.filters = { sort: 'newest', page: 1, per_page: 20 }
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.loading = true; state.error = null })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false
        state.products = action.payload.products
        state.total = action.payload.total
        state.page = action.payload.page
        state.pages = action.payload.pages
        state.per_page = action.payload.per_page
        state.availableFilters = action.payload.filters
        if (action.payload.categories?.length) {
          state.categories = action.payload.categories
        }
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false
        state.error = action.payload as string
      })
      .addCase(fetchCategories.fulfilled, (state, action) => {
        state.categories = action.payload
      })
  },
})

export const { setFilters, setPage, clearFilters } = catalogSlice.actions
export default catalogSlice.reducer
