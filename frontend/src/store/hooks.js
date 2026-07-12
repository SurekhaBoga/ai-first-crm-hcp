import { useDispatch, useSelector } from 'react-redux'

/**
 * Store-wide dispatch/selector hooks. Feature code should import these
 * instead of the raw react-redux hooks, so the store shape stays defined
 * in one place (this folder) as it grows.
 */
export const useAppDispatch = () => useDispatch()
export const useAppSelector = useSelector
