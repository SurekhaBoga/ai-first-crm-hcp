import { lazy, Suspense } from 'react'
import { createBrowserRouter } from 'react-router-dom'
import DashboardLayout from '@/layouts/DashboardLayout'
import AppShell from '@/components/AppShell'
import PageLoader from '@/components/PageLoader'
import NotFoundPage from '@/pages/NotFoundPage'

// Route-level code splitting — each page is its own chunk, fetched on
// first navigation instead of bloating the main bundle.
const LogInteractionPage = lazy(() => import('@/pages/interactions/LogInteractionPage'))
const DoctorDirectoryPage = lazy(() => import('@/pages/doctors/DoctorDirectoryPage'))
const DoctorProfilePage = lazy(() => import('@/pages/doctors/DoctorProfilePage'))
const InteractionDetailsPage = lazy(() => import('@/pages/interactions/InteractionDetailsPage'))

function withSuspense(element) {
  return <Suspense fallback={<PageLoader />}>{element}</Suspense>
}

/**
 * Trimmed to exactly what the assignment needs: the AI-first Log
 * Interaction workspace as the home/index route, the Doctor Directory it
 * depends on (HCPs must exist for the AI to resolve a name against), and
 * read-only Interaction Details (where "Save" lands). No sign-in route —
 * AppShell resolves an identity silently before rendering.
 */
export const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      {
        element: <DashboardLayout />,
        children: [
          { index: true, element: withSuspense(<LogInteractionPage />) },
          {
            path: 'doctors',
            children: [
              { index: true, element: withSuspense(<DoctorDirectoryPage />) },
              { path: ':doctorId', element: withSuspense(<DoctorProfilePage />) },
            ],
          },
          { path: 'interactions/:interactionId', element: withSuspense(<InteractionDetailsPage />) },
          { path: '*', element: <NotFoundPage /> },
        ],
      },
    ],
  },
], {
  basename: import.meta.env.BASE_URL,
})
