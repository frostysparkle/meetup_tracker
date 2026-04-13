const Login = {
    template: `
        <div class="login-form">
            <h2>Admin Login</h2>
            <form @submit.prevent="login">
                <input type="password" v-model="password" placeholder="Enter APP_PASSWORD" required>
                <button type="submit" :disabled="isLoading">
                    {{ isLoading ? 'Loading...' : 'Login' }}
                </button>
            </form>
            <div v-if="error" class="result-message error">{{ error }}</div>
        </div>
    `,
    data() {
        return {
            password: '',
            error: null,
            isLoading: false
        };
    },
    methods: {
        async login() {
            this.isLoading = true;
            this.error = null;
            try {
                const response = await axios.post(`${API_BASE_URL}/verify_password`, {
                    password: this.password
                });
                if (response.data.success) {
                    localStorage.setItem('auth', 'true');
                    this.$router.push('/app/home');
                }
            } catch (err) {
                if (err.response && err.response.data && err.response.data.error) {
                    this.error = err.response.data.error;
                } else {
                    this.error = 'An error occurred during login.';
                }
            } finally {
                this.isLoading = false;
            }
        }
    }
};
