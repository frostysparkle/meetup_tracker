const API_BASE_URL = 'http://localhost:5000/api';

const app = Vue.createApp({
    template: `
        <div>
            <Navbar v-if="isAuthenticated" />
            <div class="container">
                <router-view></router-view>
            </div>
        </div>
    `,
    computed: {
        isAuthenticated() {
            return this.$route.meta.requiresAuth;
        }
    }
});

const routes = [
    { 
        path: '/', 
        redirect: '/app/home' 
    },
    { 
        path: '/app/login', 
        component: Login,
        meta: { requiresAuth: false }
    },
    { 
        path: '/app/home', 
        component: Scanner,
        meta: { requiresAuth: true }
    },
    { 
        path: '/app/attendees', 
        component: Attendees,
        meta: { requiresAuth: true }
    }
];

const router = VueRouter.createRouter({
    history: VueRouter.createWebHashHistory(),
    routes,
});

// Navigation Guard
router.beforeEach((to, from, next) => {
    const isAuthenticated = localStorage.getItem('auth') === 'true';
    if (to.meta.requiresAuth && !isAuthenticated) {
        next('/app/login');
    } else if (to.path === '/app/login' && isAuthenticated) {
        next('/app/home');
    } else {
        next();
    }
});

app.use(router);
app.mount('#app');
