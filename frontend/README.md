# EduFlow Vue Conversion

This is your original single HTML + Vue CDN demo converted into a Vite Vue project with multiple `.vue` files.

## Run it

```bash
cd eduflow-vue-conversion
npm install
npm run dev
```

Then open the local URL shown by Vite.

## Main files

```text
src/
├── App.vue
├── main.js
├── assets/styles.css
├── data/mockData.js
├── layouts/AppShell.vue
├── components/
│   ├── Sidebar.vue
│   ├── Topbar.vue
│   ├── ToastContainer.vue
│   ├── StatCard.vue
│   ├── CourseTable.vue
│   └── UsersTable.vue
└── views/
    ├── AuthView.vue
    ├── StudentDashboard.vue
    ├── TeacherDashboard.vue
    ├── AdminDashboard.vue
    ├── CoursesView.vue
    ├── CourseDetailView.vue
    ├── NotificationsView.vue
    ├── CertificatesView.vue
    └── UsersView.vue
```

## Notes

- The mock data was moved to `src/data/mockData.js`.
- The big CSS block was moved to `src/assets/styles.css`.
- The CDN Vue script was removed because Vite imports Vue with npm.
- Chart.js is imported inside the dashboard components.
- The code still uses mock data; later you can replace it with Django API calls.
