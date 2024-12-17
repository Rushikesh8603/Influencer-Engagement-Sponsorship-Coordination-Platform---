<template>
  <div class="dashboard">
    <header>
      <h1>Sponsor</h1>
      <nav>
        <router-link to="/sponsor-home">Profile</router-link>
        <router-link to="/campaigns" class="active">Campaigns</router-link>
        <router-link to="#">Find</router-link>
        <router-link to="#">Stats</router-link>
        <router-link to="/" @click.prevent="logout">Logout</router-link>
      </nav>
    </header>
    <main>
      <h2>Edit Campaign</h2>
      <form @submit.prevent="updateCampaign" class="form-container">
        <div class="form-field">
          <label for="title"><b>Title</b></label>
          <input type="text" v-model="campaign.title" placeholder="Enter Title" required />
        </div>

        <div class="form-field">
          <label for="description"><b>Description</b></label>
          <textarea v-model="campaign.description" placeholder="Enter Description" required></textarea>
        </div>

        <div class="form-field">
          <label for="niche"><b>Niche</b></label>
          <input type="text" v-model="campaign.niche" placeholder="Enter Niche" required />
        </div>

        <div class="form-field">
          <label for="start_date"><b>Start Date</b></label>
          <input type="date" v-model="campaign.start_date" required />
        </div>

        <div class="form-field">
          <label for="end_date"><b>End Date</b></label>
          <input type="date" v-model="campaign.end_date" required />
        </div>

        <div class="form-field">
          <label for="budget"><b>Budget</b></label>
          <input type="number" v-model="campaign.budget" placeholder="Enter Budget" required />
        </div>

        <div class="form-field">
          <label for="visibility"><b>Visibility</b></label>
          <select v-model="campaign.visibility" required>
            <option value="public">Public</option>
            <option value="private">Private</option>
          </select>
        </div>

        <div class="form-actions">
          <button type="submit" class="btn add">Update</button>
        </div>
      </form>

      <div v-if="successMessage" class="success-message">{{ successMessage }}</div>
      <div v-if="errorMessage" class="error-message">{{ errorMessage }}</div>
    </main>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      campaign: {
        title: '',
        description: '',
        niche: '',
        start_date: '',
        end_date: '',
        budget: '',
        visibility: 'public'
      },
      successMessage: '',
      errorMessage: ''
    };
  },
  created() {
    this.loadCampaign();
  },
  methods: {
    async loadCampaign() {
      const { id } = this.$route.params;
      const token = localStorage.getItem('token');

      if (!token) {
        this.$router.push('/');
        return;
      }

      try {
        const response = await axios.get(`http://localhost:5000/campaigns/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.campaign = response.data;
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to load campaign details';
      }
    },

    async updateCampaign() {
      const { id } = this.$route.params;
      const token = localStorage.getItem('token');

      if (!token) {
        this.errorMessage = 'Unauthorized access. Please log in again.';
        return;
      }

      try {
        const response = await axios.put(`http://localhost:5000/campaigns/${id}/update`, this.campaign, {
          headers: { Authorization: `Bearer ${token}` }
        });
        this.successMessage = response.data.message || 'Campaign updated successfully!';
        this.$router.push('/sponsor-home');
      } catch (error) {
        this.errorMessage = error.response?.data?.error || 'Failed to update campaign. Please try again.';
      }
    },

    logout() {
      localStorage.removeItem('token');
      this.$router.push('/');
    }
  }
};
</script>

<style scoped>
@import '../styles/static/sponsor.css';
</style>
