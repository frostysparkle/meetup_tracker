const Navbar = {
    template: `
        <nav class="navbar">
            <h1>Meetup Tracker</h1>
            <div class="navbar-links">
                <router-link to="/app/home">Scanner</router-link>
                <router-link to="/app/attendees">Attendees</router-link>
                <span class="stats-badge">Present: {{ totalPresent }}</span>
                <a href="#" @click.prevent="logout" style="margin-left: 20px; color: #ff9800;">Logout</a>
            </div>
        </nav>
    `,
    data() {
        return {
            totalPresent: 0,
            interval: null
        };
    },
    mounted() {
        this.fetchStats();
        // Poll for updates every 5 seconds
        this.interval = setInterval(this.fetchStats, 5000);
    },
    unmounted() {
        if (this.interval) clearInterval(this.interval);
    },
    methods: {
        async fetchStats() {
            try {
                const response = await axios.get(`${API_BASE_URL}/stats`);
                this.totalPresent = response.data.total_present;
            } catch (error) {
                console.error("Error fetching stats:", error);
            }
        },
        logout() {
            localStorage.removeItem('auth');
            this.$router.push('/app/login');
        }
    }
};
