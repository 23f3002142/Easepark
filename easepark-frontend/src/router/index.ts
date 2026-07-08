import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
    meta: {
      title: 'EasePark — Book Parking Online | Find & Reserve Parking Near You',
      description:
        'EasePark is a smart parking app to find, reserve, and pay for parking near you in real time. Book parking online in seconds and see live availability on a map.',
    },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: {
      guest: true,
      title: 'Log In — EasePark Smart Parking App',
      description:
        'Log in to EasePark to find, book, and manage parking near you. Reserve parking spots online in real time.',
    },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: {
      guest: true,
      title: 'Sign Up — Book & Reserve Parking Online | EasePark',
      description:
        'Create a free EasePark account to book parking online, reserve spots near you, and pay only for the time you park. Sign up in seconds.',
    },
  },
  {
    path: '/forgot-password',
    name: 'forgot-password',
    component: () => import('@/pages/ForgotPasswordPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: () => import('@/pages/AuthCallbackPage.vue'),
  },

  // ─── Public marketing / legal pages (visible to everyone) ───
  {
    path: '/about',
    name: 'about',
    component: () => import('@/pages/AboutPage.vue'),
    meta: {
      title: 'About EasePark — The Smart Parking App to Book Parking Online',
      description:
        'Learn about EasePark, the smart parking platform that lets you find, reserve, and pay for parking near you in real time — and helps operators manage lots.',
    },
  },
  {
    path: '/privacy',
    name: 'privacy',
    component: () => import('@/pages/PrivacyPolicyPage.vue'),
    meta: {
      title: 'Privacy Policy — EasePark',
      description:
        'How EasePark collects, uses, and protects your data when you book and manage parking online.',
    },
  },
  {
    path: '/terms',
    name: 'terms',
    component: () => import('@/pages/TermsPage.vue'),
    meta: {
      title: 'Terms of Service — EasePark',
      description:
        'The terms that govern your use of EasePark, the online parking booking platform.',
    },
  },

  // ─── User Routes ───
  {
    path: '/dashboard',
    name: 'user-dashboard',
    component: () => import('@/pages/user/DashboardPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/profile',
    name: 'user-profile',
    component: () => import('@/pages/user/ProfilePage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/profile/edit',
    name: 'user-profile-edit',
    component: () => import('@/pages/user/ProfileEditPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/book',
    name: 'choose-booking',
    component: () => import('@/pages/user/ChooseBookingPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/book/map',
    name: 'book-map',
    component: () => import('@/pages/user/MapBookingPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/book/list',
    name: 'book-list',
    component: () => import('@/pages/user/BookSpotPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/bookings',
    name: 'booking-history',
    component: () => import('@/pages/user/BookingHistoryPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/vehicles',
    name: 'user-vehicles',
    component: () => import('@/pages/user/MyVehiclesPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/release/:id',
    name: 'release-spot',
    component: () => import('@/pages/user/ReleaseSpotPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/summary',
    name: 'user-summary',
    component: () => import('@/pages/user/SummaryPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },
  {
    path: '/notifications',
    name: 'user-notifications',
    component: () => import('@/pages/user/NotificationsPage.vue'),
    meta: { requiresAuth: true, role: 'user' },
  },

  {
    path: '/change-password',
    name: 'change-password',
    component: () => import('@/pages/ChangePasswordPage.vue'),
    meta: { requiresAuth: true },
  },

  // ─── Admin Routes ───
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('@/pages/admin/DashboardPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/profile',
    name: 'admin-profile',
    component: () => import('@/pages/admin/ProfilePage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/profile/edit',
    name: 'admin-profile-edit',
    component: () => import('@/pages/admin/ProfileEditPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/lots/add',
    name: 'admin-add-lot',
    component: () => import('@/pages/admin/AddLotPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/lots/:id/edit',
    name: 'admin-edit-lot',
    component: () => import('@/pages/admin/EditLotPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/users',
    name: 'admin-users',
    component: () => import('@/pages/admin/UsersPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/users/:id/history',
    name: 'admin-user-history',
    component: () => import('@/pages/admin/UserHistoryPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/search',
    name: 'admin-search',
    component: () => import('@/pages/admin/SearchPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
  {
    path: '/admin/summary',
    name: 'admin-summary',
    component: () => import('@/pages/admin/SummaryPage.vue'),
    meta: { requiresAuth: true, role: 'admin' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to) {
    if (to.hash) {
      return { el: to.hash, behavior: 'smooth' }
    }
    return { top: 0 }
  },
})

router.beforeEach(async (to, _from, next) => {
  const authStore = useAuthStore()

  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchProfile()
  }

  if (to.meta.guest && authStore.isAuthenticated) {
    if (authStore.isAdmin) return next({ name: 'admin-dashboard' })
    return next({ name: 'user-dashboard' })
  }

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    return next({ name: 'login' })
  }

  if (to.meta.role && authStore.user?.role !== to.meta.role) {
    if (authStore.isAdmin) return next({ name: 'admin-dashboard' })
    if (authStore.isUser) return next({ name: 'user-dashboard' })
    return next({ name: 'home' })
  }

  next()
})

// ── Per-page SEO: set <title>, meta description, and canonical on each route ──
// Google renders our JS, so these client-side updates are picked up for indexing.
const SITE_ORIGIN = 'https://easepark.app'
const DEFAULT_TITLE = 'EasePark — Book Parking Online | Find & Reserve Parking Near You'
const DEFAULT_DESCRIPTION =
  'EasePark is a smart parking app to find, reserve, and pay for parking near you in real time. Book parking online in seconds and see live availability on a map.'

function upsertMeta(name: string, content: string) {
  let el = document.head.querySelector<HTMLMetaElement>(`meta[name="${name}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute('name', name)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function upsertCanonical(href: string) {
  let el = document.head.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', 'canonical')
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

router.afterEach((to) => {
  const title = (to.meta.title as string) || DEFAULT_TITLE
  const description = (to.meta.description as string) || DEFAULT_DESCRIPTION
  document.title = title
  upsertMeta('description', description)
  // Canonical always points at the apex, no trailing slash except root
  upsertCanonical(SITE_ORIGIN + (to.path === '/' ? '/' : to.path))
})

export default router
