<template>
  <div class="dashboard">
    <header>
      <h1>Sponsor</h1>
      <nav>
        <router-link to="/sponsor-home">Profile</router-link>
        <router-link to="/campaign">Campaigns</router-link>
        <router-link to="/influencer_requests">Requested</router-link>
        <a href="#" @click.prevent="triggerMonthlyReport">Monthly Report</a>
        <router-link to="/Export"> Export as CSV</router-link>
        <router-link to="/">Logout</router-link>
      </nav>

    </header>

    <main>
      <section class="welcome">
        <h2>Welcome <b>{{ userName }}!!</b></h2>

        <div v-if="campaigns.length === 0">
          <p>No campaigns found. Create one to get started!</p>
        </div>

        <div v-for="campaign in campaigns" :key="campaign.id" class="campaign">
          <div class="campaign-details">
            <div class="detail">
              <span id="R">Title:</span>
              <span>{{ campaign.title }}</span>
            </div>
            <div class="detail">
              <span id="R">Description:</span>
              <span>{{ campaign.description }}</span>
            </div>
            <div class="detail">
              <span id="R">Niche:</span>
              <span>{{ campaign.niche }}</span>
            </div>
            <div class="detail">
              <span id="R">Start Date:</span>
              <span>{{ campaign.start_date }}</span>
            </div>
            <div class="detail">
              <span id="R">End Date:</span>
              <span>{{ campaign.end_date }}</span>
            </div>
            <div class="detail">
              <span id="R">Budget:</span>
              <span>{{ campaign.budget }}</span>
            </div>
            <div class="detail">
              <span id="R">Visibility:</span>
              <span>{{ campaign.visibility }}</span>
            </div>
          </div>

          <div class="campaign-actions">
            <button style="padding: 5px; background-color: green; color: white;" @click="Hire(campaign.id)" class="view-btn">Hire influencer</button>
            <button style="padding-left: 10px; margin-right: 10px;" @click="editCampaign(campaign.id)" class="view-btn">Update</button>
            <button style="padding-left: 10px;" @click="deleteCampaign(campaign.id)" class="delete-btn">Delete</button>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      userName: '', // Will be set after fetching from API
      searchQuery: '',
      campaigns: [] // Holds the fetched campaigns
    };
  },
  created() {
    this.fetchCampaigns();
  },
  methods: {
    async triggerMonthlyReport() {
      try {
        const response = await axios.post("http://localhost:5000/send-monthly-report");
        alert(response.data.message); // Notify the user that the report task has started
      } catch (error) {
        console.error("Error triggering monthly report:", error);
        alert("Failed to trigger the monthly report.");
      }
    },
    async fetchCampaigns() {
      try {
        const token = localStorage.getItem('token'); // Get JWT token from localStorage

        if (!token) {
          this.$router.push('/'); // Redirect to login if token is not present
          return;
        }

        const response = await axios.get('http://localhost:5000/sponsor-home', {
          headers: {
            Authorization: `Bearer ${token}` // Pass the token in Authorization header
          }
        });

        // Set the user name and campaigns data from the response
        this.userName = response.data.user_name;
        this.campaigns = response.data.campaigns;
      } catch (error) {
        console.error("Error fetching campaigns:", error);
        if (error.response) {
          alert(error.response.data.error || "Error fetching campaigns");
        }
      }
    },

    searchInfluencers() {
      console.log("Searching for:", this.searchQuery);
      // Add actual search functionality here if needed
    },

    async deleteCampaign(id) {
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`http://localhost:5000/dcampaign/${id}`, {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });
        this.campaigns = this.campaigns.filter(campaign => campaign.id !== id);
        alert("Campaign deleted successfully!");
      } catch (error) {
        console.error("Error deleting campaign:", error);
        alert("Failed to delete campaign");
      }
    },

    editCampaign(id) {
      this.$router.push({ name: 'EditCampaign', params: { id } });
    },

    Hire(id) {
      this.$router.push({ name: 'search_influ_from_spo', params: { id } });

    }
  }
};
</script>

<style scoped>
@import '../styles/static/sponsor.css';
.welcome{
  padding-bottom: 100px;
}
/* Additional styles for the sponsor dashboard */
</style>
