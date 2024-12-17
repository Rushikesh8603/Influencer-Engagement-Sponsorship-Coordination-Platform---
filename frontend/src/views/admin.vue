<template>
  <div class="admin-page">
    <!-- Navbar -->
    <nav class="navbar">
      <h1 class="navbar-title">Admin Dashboard</h1>
      <router-link to="/" @click="logout"><b>logout</b></router-link>
    </nav>

    <!-- Main Content -->
    <div class="content">
      <!-- Show Stats Section -->
      <section id="show-stats" class="card">
        <h2>Sponsors Vs Influencers</h2>
        <canvas id="userStatsChart"></canvas>
      </section>

      <!-- Campaign Visibility Section -->
      <section id="access-management" class="card">
        <h2>Campaigns</h2>
        <p>Public Vs Private</p>
        <canvas id="campaignChart" width="400" height="200"></canvas>
      </section>

      <!-- Accepted Vs Rejected by Sponsors (Pie Chart) -->
      <section id="flag" class="card">
        <h2>Accepted Vs Rejected by Influencers </h2>
        <canvas id="sponsorPieChart"></canvas>
      </section>

      <!-- Accepted Vs Rejected by Influencers (Pie Chart) -->
      <section id="campaign-user" class="card">
        <h2>Accepted Vs Rejected by Sponsors</h2>
        <canvas id="influencerPieChart"></canvas>
      </section>

      <section id="show-stats" class="card">
        <h2>Approve Sponsors</h2>
        <div class="sponsor-table">
          <div class="sponsor-heading">
            <div>Name</div>
            <div>Role</div>
            <div>Company Name</div>
            <div>Industry</div>
            <div>Budget</div>
            <div>Action</div>
          </div>
          <div v-for="sponsor in sponsors" :key="sponsor.id" class="sponsor-row">
            <div>{{ sponsor.username }}</div>
            <div>{{ sponsor.role }}</div>
            <div>{{ sponsor.company_name }}</div>
            <div>{{ sponsor.industry }}</div>
            <div>${{ sponsor.budget }}</div>
            <div>
              <button :class="sponsor.approve ? 'btn-approved' : 'btn-approve'" @click="toggleApprove(sponsor.id)">
                {{ sponsor.approve ? "Disapprove" : "Approve" }}
              </button>
            </div>
          </div>
        </div>
      </section>
      <section id="show-stats" class="card">
        <h2>Flag Sponsors / Influencers</h2>
        <table>
          <thead>
            <tr>
              <th>Username</th>
              <th>Role</th>
              <th>Flag</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in users" :key="user.id">
              <td>{{ user.username }}</td>
              <td>{{ user.role }}</td>
              <td>{{ user.flag ? "User Flagged" : "Not Flagged" }}</td>
              <td>
                <button @click="toggleFlag(user.id, !user.flag)">
                  {{ user.flag ? "Unflag" : "Flag" }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

    </div>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "AdminPage",
  data() {
    return {
      sponsors: [], // To store sponsor data
      users: [],

    };
  },
  mounted() {
    this.renderChart();
    this.fetchSponsors(); // Load sponsors when component is mounted
    this.renderChart();
    this.fetchUsers();

  },
  methods: {
    async fetchSponsors() {
      try {
        const response = await axios.get("http://localhost:5000/sponsors");
        this.sponsors = response.data; // Assuming the backend returns an array of sponsors
      } catch (error) {
        console.error("Error fetching sponsors:", error);
      }
    },
    async toggleApprove(sponsorId) {
      try {
        const sponsor = this.sponsors.find((s) => s.id === sponsorId);
        sponsor.approve = !sponsor.approve; // Toggle approval status locally
        await axios.put(`http://localhost:5000/api/sponsors/${sponsorId}`, {
          approve: sponsor.approve,
        });
      } catch (error) {
        console.error("Error updating approval status:", error);
      }
    },
    async fetchUsers() {
      try {
        const response = await axios.get("http://localhost:5000/userss");
        this.users = response.data;
      } catch (error) {
        console.error("Error fetching users:", error);
      }
    },
    async toggleFlag(userId, flag) {
      try {
        const response = await axios.put(
          `http://localhost:5000/api/users/${userId}`,
          { flag }
        );
        console.log(response.data.message);
        this.fetchUsers(); // Refresh the list after toggling
      } catch (error) {
        console.error("Error updating flag status:", error);
      }
    },
    async renderChart() {
      try {
        // Fetch data from the backend
        const response = await axios.get("http://localhost:5000/api/user-stats");
        const data = response.data;

        // Chart 1: Sponsors Vs Influencers (Bar Chart)
        const ctx1 = document.getElementById("userStatsChart").getContext("2d");
        new Chart(ctx1, {
          type: "bar",
          data: {
            labels: ["Influencers", "Sponsors"],
            datasets: [
              {
                label: "User Count",
                data: [data.influencers, data.sponsors],
                backgroundColor: ["#42a5f5", "#66bb6a"],
                borderColor: ["#1e88e5", "#43a047"],
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                display: true,
                position: "top",
              },
            },
            scales: {
              y: {
                beginAtZero: true,
                title: {
                  display: true,
                  text: "Number of Users",
                },
              },
              x: {
                title: {
                  display: true,
                  text: "Roles",
                },
              },
            },
          },
        });

        // Chart 2: Public Vs Private Campaigns (Bar Chart)
        const ctx2 = document.getElementById("campaignChart").getContext("2d");
        new Chart(ctx2, {
          type: "bar",
          data: {
            labels: ["Public Campaigns", "Private Campaigns"],
            datasets: [
              {
                label: "Campaign Visibility",
                data: [data.public_campaigns, data.private_campaigns],
                backgroundColor: ["#4caf50", "#f44336"],
                borderColor: ["#4caf50", "#f44336"],
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            scales: {
              y: {
                beginAtZero: true,
              },
            },
          },
        });

        // Chart 3: Accepted Vs Rejected by Sponsors (Pie Chart)
        const ctx3 = document.getElementById("sponsorPieChart").getContext("2d");
        new Chart(ctx3, {
          type: "pie",
          data: {
            labels: ["Accepted by Sponsors", "Rejected by Sponsors"],
            datasets: [
              {
                label: "Sponsor Responses",
                data: [
                  data.influencers_accepted_adreqeust,
                  data.influencers_rejected_adreqeust,
                ],
                backgroundColor: ["#66bb6a", "#f44336"],
                borderColor: ["#43a047", "#e53935"],
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: "top",
              },
              tooltip: {
                callbacks: {
                  label: (tooltipItem) => {
                    return `${tooltipItem.label}: ${tooltipItem.raw}`;
                  },
                },
              },
            },
          },
        });

        // Chart 4: Accepted Vs Rejected by Influencers (Pie Chart)
        const ctx4 = document.getElementById("influencerPieChart").getContext("2d");
        new Chart(ctx4, {
          type: "pie",
          data: {
            labels: ["Accepted by Influencers", "Rejected by Influencers"],
            datasets: [
              {
                label: "Influencer Responses",
                data: [
                  data.sponsor_accepted_adreqeust,
                  data.sponsor_rejected_adreqeust,
                ],
                backgroundColor: ["#66bb6a", "#f44336"],
                borderColor: ["#43a047", "#e53935"],
                borderWidth: 1,
              },
            ],
          },
          options: {
            responsive: true,
            plugins: {
              legend: {
                position: "top",
              },
              tooltip: {
                callbacks: {
                  label: (tooltipItem) => {
                    return `${tooltipItem.label}: ${tooltipItem.raw}`;
                  },
                },
              },
            },
          },
        });
      } catch (error) {
        console.error("Error loading chart data:", error);
      }
    },
  },
  logout() {
    this.$router.push('/');
  }
};
</script>

<style scoped>
@import "../styles/static/admin.css";

/* Optional: Styling for the charts container */
</style>
