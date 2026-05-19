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
        path: 'admin-dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/AdminDashboard.vue'),
        meta: { role: 'admin' }
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
       path: 'student-courses',
       name: 'StudentCourses',
       component: () => import('@/views/StudentCourses.vue'),
       meta: { role: 'student' }
      },
      {
       path: 'student-courses/:id',
       name: 'StudentCourseDetail',
       component: () => import('@/views/StudentCourseDetail.vue'),
       meta: { role: 'student' }
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