// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/AuthView.vue'),
    meta: { requiresAuth: false }
  },

  {
    path: '/',
    component: () => import('@/layouts/AppShell.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/teacher-dashboard'
      },
      {
        path: 'student-dashboard',
        name: 'StudentDashboard',
        component: () => import('@/views/StudentDashboard.vue'),
        meta: { role: 'student' }
      },
      {
        path: 'admin-dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/AdminDashboard.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'users',
        name: 'Users',
        component: () => import('@/views/UsersView.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'admin-courses',
        name: 'AdminCourses',
        component: () => import('@/views/AdminCoursesView.vue'),
        meta: { role: 'admin' }
      },
      {
        path: 'reports',
        name: 'AdminReports',
        component: () => import('@/views/AdminReportsView.vue'),
        meta: {
          requiresAuth: true,
          role: 'admin',
        },
      },
      {
        path: 'certificates',
        name: 'Certificates',
        component: () => import('@/views/CertificatesView.vue'),
        meta: {
          requiresAuth: true,
          role: 'student'
        }
      },
      {
        path: 'continue-learning',
        name: 'ContinueLearning',
        component: () => import('@/views/ContinueLearningView.vue'),
        meta: {
          requiresAuth: true,
          role: 'student'
        }
      },
      {
        path: 'teacher-dashboard',
        name: 'TeacherDashboard',
        component: () => import('@/views/TeacherDashboard.vue'),
        meta: { role: 'teacher' }
      },
      {
        path: 'create-course',
        name: 'CreateCourse',
        component: () => import('@/views/CreateCourse.vue'),
        meta: { role: 'teacher' }
      },
      {
        path: '/courses/:id/edit',
        name: 'EditCourse',
        component: () => import('@/views/CreateCourse.vue'),
        meta: { role: 'teacher' }
      },
      {
        path: 'courses',
        name: 'Courses',
        component: () => import('@/views/CoursesView.vue')
      },
      {
        path: 'courses/:id',
        name: 'CourseDetail',
        component: () => import('@/views/CourseDetailView.vue')
      },
      {
        path: '/assignments',
        name: 'assignments',
        component: () => import('@/views/AssignmentsView.vue'),
      },
      {
        path: '/quizzes',
        name: 'quizzes',
        component: () => import('@/views/QuizzesView.vue'),
      },
      {
        path: 'explore-courses',
        name: 'ExploreCourses',
        component: () => import('@/views/ExploreCourses.vue'),
        meta: { role: 'student' }
      },
      {
        path: '/student/quizzes',
        name: 'StudentQuizzes',
        component: () => import('@/views/StudentQuizzesView.vue'),
      },
      {
        path: '/student/assignments',
        name: 'StudentAssignments',
        component: () => import('@/views/StudentAssignmentsView.vue'),
      },
      {
        path: '/courses/:id/edit',
        component: () => import('@/views/CreateCourse.vue'),
      },
      {
        path: 'student-stats',
        name: 'StudentStats',
        component: () => import('@/views/StudentsStatsView.vue'),
        meta: { role: 'teacher' }
      },
      {
        path: 'course-performance',
        name: 'CoursePerformance',
        component: () => import('@/views/CoursePerformance.vue'),
        meta: { role: 'teacher' }
      },
      {
        path: 'notifications',
        name: 'Notifications',
        component: () => import('@/views/NotificationsView.vue'),
        meta: { role: 'teacher' }
      }
    ]
  },

  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router