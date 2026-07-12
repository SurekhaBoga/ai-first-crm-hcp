import axios from 'axios'

/**
 * Single configured Axios instance for the whole app. Every request
 * function in src/api/* is built on this — nothing else constructs its
 * own axios/fetch call, so base URL, headers, and timeout are governed
 * from exactly one place.
 *
 * No Authorization header: the backend has no auth layer (see
 * src/store/slices/authSlice.js — "sign in" here just selects which
 * existing User record is acting, it isn't a credentialed session).
 */
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 20_000,
})

export default apiClient
