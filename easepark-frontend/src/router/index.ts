import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth.store'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/LoginPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/RegisterPage.vue'),
    meta: { guest: true },
  },
  {
    path: '/auth/callback',
    name: 'auth-callback',
    component: () => import('@/pages/AuthCallbackPage.vue'),
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

export default router
