import { MutationCache, QueryCache, QueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { getApiErrorMessage } from '@/api/errors'

/**
 * One QueryClient for the whole app. Errors are toasted here, globally,
 * so individual hooks only need an onError when they want to do
 * something *beyond* notifying the user (rare) — see src/hooks/queries/*.
 * Mutation errors always toast; query errors only toast once a query has
 * data to protect (avoids double-toasting a first-load failure that the
 * page's own error state already renders).
 */
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
      refetchOnWindowFocus: false,
    },
    mutations: {
      retry: 0,
    },
  },
  queryCache: new QueryCache({
    onError: (error, query) => {
      if (query.state.data !== undefined) {
        toast.error(getApiErrorMessage(error))
      }
    },
  }),
  mutationCache: new MutationCache({
    onError: (error) => {
      toast.error(getApiErrorMessage(error))
    },
  }),
})
