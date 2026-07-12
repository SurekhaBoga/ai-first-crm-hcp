/**
 * The backend returns errors in one of two shapes:
 *  - domain errors (app.core.exceptions.AppError subclasses): {"detail": "some message"}
 *  - Pydantic/FastAPI validation errors (422):
 *      {"detail": [{"loc": [...], "msg": "...", "type": "..."}, ...]}
 * This is the one place that distinction is handled, so every mutation's
 * onError can just call this and toast the result.
 */
export function getApiErrorMessage(error) {
  const detail = error?.response?.data?.detail

  if (typeof detail === 'string') return detail

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        const field = Array.isArray(item.loc) ? item.loc.at(-1) : null
        return field ? `${field}: ${item.msg}` : item.msg
      })
      .join('; ')
  }

  if (error?.code === 'ECONNABORTED') return 'The request timed out. Please try again.'
  if (error?.message === 'Network Error') return 'Cannot reach the server. Check your connection and try again.'

  return error?.message || 'Something went wrong. Please try again.'
}
