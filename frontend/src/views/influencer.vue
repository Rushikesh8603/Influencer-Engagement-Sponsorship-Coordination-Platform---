<template>
  <div class="dashboard">
    <header>
      <h1>Influencer's Profile</h1>
      <nav>
        <router-link to="/iDash">Profile</router-link>
        <router-link to="/active-campaigns">Active Campaigns</router-link>
        <router-link to="/sponsor_request">Sponsor Request</router-link>
        <router-link to="/" @click="logout">Logout</router-link>
      </nav>
    </header>
    <main>
      <section class="welcome">
        <h2>Welcome <b>{{ profileData.username }} (❁´◡`❁)</b></h2>
        <div class="profile-card">
          <h3 class="profile-name">{{ profileData.username }}</h3>
          <p class="profile-role">{{ profileData.role }}</p>
          <div class="profile-details">
            <div class="detail">
              <span class="detail-title">Category:</span>
              <span class="detail-value">{{ profileData.category }}</span>
            </div>
            <div class="detail">
              <span class="detail-title">Niche:</span>
              <span class="detail-value">{{ profileData.niche }}</span>
            </div>
            <div class="detail">
              <span class="detail-title">Reach:</span>
              <span class="detail-value">{{ profileData.reach }}K</span>
            </div>
          </div>
          <button class="update-btn" @click="openUpdateModal">Update Profile</button>
        </div>
      </section>
    </main>

    <!-- Update Profile Modal -->
    <div class="modal" v-if="showUpdateModal">
      <div class="modal-content">
        <h3>Update Profile</h3>
        <form @submit.prevent="updateProfile">
          <label>
            Username:
            <input type="text" v-model="updatedProfile.username" required />
          </label>
          <label>
            Category:
            <input type="text" v-model="updatedProfile.category" required />
          </label>
          <label>
            Niche:
            <input type="text" v-model="updatedProfile.niche" required />
          </label>
          <label>
            Reach (in K):
            <input type="number" v-model="updatedProfile.reach" required />
          </label>
          <button type="submit" class="submit-btn">Save Changes</button>
          <button type="button" class="cancel-btn" @click="closeUpdateModal">Cancel</button>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      profileData: {}, // Holds fetched profile data
      updatedProfile: {}, // Holds updated profile data for the form
      showUpdateModal: false // Controls visibility of the update modal
    };
  },
  created() {
    this.fetchProfile();
  },
  methods: {
    async fetchProfile() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get('http://localhost:5000/influencer-profile', {
          headers: {
            Authorization: `Bearer ${token}`
          }
        });

        this.profileData = response.data.profile;
        this.profileData.username = response.data.username;
      } catch (error) {
        console.error("Error fetching profile:", error);
        if (error.response) {
          alert(error.response.data.message || "Error fetching profile");
        }
      }
    },
    openUpdateModal() {
      // Prepopulate the update form with current profile data
      this.updatedProfile = { ...this.profileData };
      this.showUpdateModal = true;
    },
    closeUpdateModal() {
      this.showUpdateModal = false;
    },
    async updateProfile() {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.put(
          'http://localhost:5000/update-influencer-profile',
          this.updatedProfile,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        if (response.status === 200) {
          alert('Profile updated successfully!');
          this.profileData = { ...this.updatedProfile }; // Update the UI with the new data
          this.showUpdateModal = false;
        }
      } catch (error) {
        console.error("Error updating profile:", error);
        alert("Failed to update profile. Please try again.");
      }
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/');
    }
  }
};
</script>

<style>
/* Update Modal Styling */

  @import '../styles/static/influ_profile.css';
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}
.modal-content {
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  width: 400px;
}
label {
  display: block;
  margin: 10px 0;
}
input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  margin-top: 15px;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
.update-btn {
  background: #007bff;
  color: #fff;
}
.submit-btn {
  background: #28a745;
  color: #fff;
}
.cancel-btn {
  background: #dc3545;
  color: #fff;
}


</style>

