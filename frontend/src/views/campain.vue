<template>
  <div class="dashboard">
    <header>
      <h1>Sponsor</h1>
      <nav>
        <a href="/sponsor-home">Profile</a>
        <a href="/campaign" class="active">Campaigns</a>
        <a href="#">Find</a>
        <a href="#">Stats</a>
        <a href="/" @click.prevent="logout">Logout</a>
      </nav>
    </header>
    <main>
      <h2>Add Campaign</h2>
      <form @submit.prevent="submitCampaign" class="form-container">
        <label for="title"><b>Title</b></label>
        <input type="text" v-model="campaign.title" placeholder="Enter Title" required />

        <label for="description"><b>Description</b></label>
        <textarea id = "Rushi" v-model="campaign.description" placeholder="Enter Description" required></textarea>

        <label for="niche"><b>Niche</b></label>
        <input type="text" v-model="campaign.niche" placeholder="Enter Niche" required />

        <label for="start_date"><b>Start Date</b></label>
        <input type="date" v-model="campaign.start_date" required />

        <label for="end_date"><b>End Date</b></label>
        <input type="date" v-model="campaign.end_date" required />

        <label for="budget"><b>Budget</b></label>
        <input type="number" v-model="campaign.budget" placeholder="Enter Budget" required />

        <label for="visibility"><b>Visibility</b></label>
        <select v-model="campaign.visibility" required>
          <option value="public">Public</option>
          <option value="private">Private</option>
        </select>

        <button type="submit" class="btn add">Add</button>
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
        budget: null,
        visibility: 'public'
      },
      successMessage: '',
      errorMessage: ''
    };
  },
  methods: {
  async submitCampaign() {
    try {
      this.successMessage = '';
      this.errorMessage = '';

      const token = localStorage.getItem('token');

      if (!token) {
        this.errorMessage = 'Unauthorized access. Please log in again.';
        return;
      }

      console.log("Submitting campaign:", this.campaign); // Log campaign data for debugging

      const response = await axios.post(
        'http://localhost:5000/campaign',
        this.campaign,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );

      this.successMessage = response.data.message || 'Campaign added successfully!';
      this.$router.push('/sponsor-home');
      this.campaign = { title: '', description: '', niche: '', start_date: '', end_date: '', budget: null, visibility: 'public' };
    } catch (error) {
      if (error.response) {
        this.errorMessage = error.response?.data?.error || 'Failed to add campaign. Please try again.';
      } else if (error.request) {
        this.errorMessage = 'Network error. Please try again later.';
      } else {
        this.errorMessage = error.message || 'An unexpected error occurred.';
      }
      console.error('Campaign submission error:', this.errorMessage);
    }
  }
}

};
</script>

<style>
@import '../styles/static/campain.css';

.dashboard {
  width: 90%;
  max-width: 1000px;
  margin: 0 auto;
  background-color: #fff;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
  border-radius: 12px;
  overflow: hidden;
  padding: 20px;
  overflow-y: auto;
}

.form-container {
  max-height: 70vh;
  overflow-y: auto;
  padding-bottom: 100px;
}

.success-message {
  color: green;
  margin-top: 10px;
}

.error-message {
  color: red;
  margin-top: 10px;
}

select, input[type="text"], input[type="number"], input[type="date"] {
  width: 100%;
  padding: 8px;
  margin: 8px 0;
  box-sizing: border-box;
  border: 2px solid #ccc;
  border-radius: 5px;
}

textarea {
  height: 150px; /* Increase height for a larger text area */
  resize: vertical; /* Allows resizing vertically if needed */
  padding: 80px;
}

#Rushi{
  padding: 30px;
}

button[type="submit"] {
  background-color: #4dabf7;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
  transition: background-color 0.3s;
}

button[type="submit"]:hover {
  background-color: #ff922b;
}
</style>
