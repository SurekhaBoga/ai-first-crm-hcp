/**
 * Shared optimistic-delete behavior for the three "delete from a Page<T>
 * list" mutations (users, doctors, interactions): remove the item from
 * every cached list matching `listKeyPrefix` immediately, and roll back
 * to the exact previous cache contents if the request fails — e.g. the
 * RESTRICT case on deleting a user who has logged interactions.
 *
 * Returns the `onMutate`/`onError` pair to spread into `useMutation`;
 * the caller still owns its own `onSuccess` (toast) and should call
 * `invalidateAfterSettle` from its `onSettled` to reconcile with the
 * server afterward.
 */
export function buildOptimisticDeleteHandlers({ queryClient, listKeyPrefix, getItemId }) {
  return {
    onMutate: async (deletedId) => {
      await queryClient.cancelQueries({ queryKey: listKeyPrefix })
      const previousQueries = queryClient.getQueriesData({ queryKey: listKeyPrefix })

      queryClient.setQueriesData({ queryKey: listKeyPrefix }, (old) => {
        if (!old?.items) return old
        return {
          ...old,
          items: old.items.filter((item) => getItemId(item) !== deletedId),
          total: Math.max(0, old.total - 1),
        }
      })

      return { previousQueries }
    },
    onError: (_error, _deletedId, context) => {
      context?.previousQueries?.forEach(([queryKey, data]) => {
        queryClient.setQueryData(queryKey, data)
      })
    },
  }
}

/**
 * Invalidates every cached query under `listKeyPrefix` except the ones
 * listed in `excludeKeys` (e.g. the deleted item's own detail/timeline
 * queries). A detail page for the deleted item may still be mid-unmount
 * when this runs — invalidating its query would refetch a resource that
 * the server has already deleted and get back a 404. Excluding it instead
 * of removing it outright means no forced refetch either way; the query
 * is simply garbage-collected once its last observer unmounts.
 */
export function invalidateAfterSettle(queryClient, listKeyPrefix, excludeKeys = []) {
  queryClient.invalidateQueries({
    queryKey: listKeyPrefix,
    predicate: (query) => !excludeKeys.some((key) => matchesKey(query.queryKey, key)),
  })
}

function matchesKey(queryKey, key) {
  return key.length === queryKey.length && key.every((part, index) => part === queryKey[index])
}
