const Attendees = {
    template: `
        <div class="attendees-container">
            <h2>Present Attendees</h2>
            <div v-if="isLoading">Loading...</div>
            <div v-else-if="error" class="result-message error">{{ error }}</div>
            <table v-else-if="attendees.length > 0">
                <thead>
                    <tr>
                        <th>Name</th>
                        <th>Email</th>
                        <th>Check-in Time</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="attendee in attendees" :key="attendee.id">
                        <td>{{ attendee.name }}</td>
                        <td>{{ attendee.smail }}</td>
                        <td>{{ new Date(attendee.created_at).toLocaleString() }}</td>
                    </tr>
                </tbody>
            </table>
            <div v-else>No attendees present yet.</div>
        </div>
    `,
    data() {
        return {
            attendees: [],
            isLoading: true,
            error: null
        };
    },
    mounted() {
        this.fetchAttendees();
    },
    methods: {
        async fetchAttendees() {
            this.isLoading = true;
            try {
                const response = await axios.get(`${API_BASE_URL}/attendees`);
                this.attendees = response.data;
            } catch (err) {
                this.error = "Failed to load attendees.";
                console.error(err);
            } finally {
                this.isLoading = false;
            }
        }
    }
};
