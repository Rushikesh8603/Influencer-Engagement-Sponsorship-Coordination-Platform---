<template>
  <div class="dashboard">
    <!-- Header and Navigation -->
    <header>
      <h1>Influencer's Profile</h1>
      <nav>
        <router-link to="/iDash">Profile</router-link>
        <router-link to="/active-campaigns">Active Campaigns</router-link>
        <router-link to="/sponsor_request">Sponsor Request</router-link>
        <router-link to="/" @click="logout">Logout</router-link>
      </nav>
    </header>

    <!-- Campaign List -->
    <section class="campaign-list">
      <h2>Pending Campaigns</h2>
      <div v-if="pendingCampaigns.length === 0" class="no-campaigns">No pending campaigns found.</div>
      <div v-else class="campaign-cards">
        <div class="campaign-card" v-for="campaign in pendingCampaigns" :key="campaign.id">
          <h3>{{ campaign.title }}</h3>
          <p><strong>Niche:</strong> {{ campaign.niche }}</p>
          <p><strong>Description:</strong> {{ campaign.description }}</p>
          <p><strong>Budget:</strong> ${{ campaign.budget }}</p>
          <p><strong>Start Date:</strong> {{ new Date(campaign.start_date).toLocaleDateString() }}</p>
          <p><strong>End Date:</strong> {{ new Date(campaign.end_date).toLocaleDateString() }}</p>
          <div class="action-buttons">
            <button class="accept-btn" @click="updateStatus('accepted', campaign.id)">Accept</button>
            <button class="reject-btn" @click="updateStatus('rejected', campaign.id)">Reject</button>
            <button class="negotiate-btn" @click="openChat(campaign.id)">Negotiate</button>
          </div>
        </div>
      </div>
    </section>

    <section class="campaign-list">
      <h2>Accepted Campaigns</h2>
      <div v-if="acceptedCampaigns.length === 0" class="no-campaigns">No accepted campaigns found.</div>
      <div v-else class="campaign-cards">
        <div class="campaign-card" v-for="campaign in acceptedCampaigns" :key="campaign.id">
          <h3>{{ campaign.title }}</h3>
          <p><strong>Niche:</strong> {{ campaign.niche }}</p>
          <p><strong>Description:</strong> {{ campaign.description }}</p>
          <p><strong>Budget:</strong> ${{ campaign.budget }}</p>
          <p><strong>Start Date:</strong> {{ new Date(campaign.start_date).toLocaleDateString() }}</p>
          <p><strong>End Date:</strong> {{ new Date(campaign.end_date).toLocaleDateString() }}</p>
        </div>
      </div>
    </section>

    <section class="campaign-list">
      <h2>Rejected Campaigns</h2>
      <div v-if="rejectedCampaigns.length === 0" class="no-campaigns">No rejected campaigns found.</div>
      <div v-else class="campaign-cards">
        <div class="campaign-card" v-for="campaign in rejectedCampaigns" :key="campaign.id">
          <h3>{{ campaign.title }}</h3>
          <p><strong>Niche:</strong> {{ campaign.niche }}</p>
          <p><strong>Description:</strong> {{ campaign.description }}</p>
          <p><strong>Budget:</strong> ${{ campaign.budget }}</p>
          <p><strong>Start Date:</strong> {{ new Date(campaign.start_date).toLocaleDateString() }}</p>
          <p><strong>End Date:</strong> {{ new Date(campaign.end_date).toLocaleDateString() }}</p>
        </div>
      </div>
    </section>



    <!-- Chatbox -->
    <div v-if="isChatOpen" class="chatbox">
      <div class="chat-header">
        <h3>Chat with Sponsor</h3>
        <button @click="closeChat" class="close-chat-btn">X</button>
      </div>
      <div class="chat-messages">
        <div v-for="message in messages" :key="message.id" class="chat-message">
          <div
            :class="{ 'sender-message': message.sender_role === 'sponsor', 'influencer-message': message.sender_role === 'influencer' }">
            <strong>{{ message.sender_role === 'sponsor' ? 'Sponsor:' : 'influencer:' }}</strong> {{ message.text }}
          </div>
        </div>
      </div>
      <div class="chat-input-container">
        <textarea v-model="chatMessage" placeholder="Type your message..." rows="3"></textarea>
        <button @click="sendMessage" class="send-btn">Send</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      campaigns: [],
      isChatOpen: false,
      messages: [],
      chatMessage: '',
      currentCampaignId: null,
      status: '',
      pendingCampaigns: [],
      acceptedCampaigns: [],
      rejectedCampaigns: [],
    };
  },
  created() {
    this.fetchCampaigns();
  },
  methods: {
  closeChat() {
    this.isChatOpen = false; // Set isChatOpen to false to hide the chatbox
  },

  openChat(campaignId) {
    // Set the current campaign id
    this.currentCampaignId = campaignId;
    this.isChatOpen = true; // Open the chatbox
    this.fetchMessages(campaignId); // Fetch messages for the selected campaign
  },
    async fetchCampaigns() {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          console.error('No token found in localStorage');
          return;
        }

        const response = await axios.get('http://localhost:5000/influencer/campaigns', {
          headers: { Authorization: `Bearer ${token}` },
        });

        // Destructure response data for better readability
        const { pending = [], accepted = [], rejected = [] } = response.data;

        // Assign the data to component's variables
        this.pendingCampaigns = pending;
        this.acceptedCampaigns = accepted;
        this.rejectedCampaigns = rejected;

        // Debugging logs for verifying data
        console.log('Pending Campaigns:', this.pendingCampaigns);
        console.log('Accepted Campaigns:', this.acceptedCampaigns);
        console.log('Rejected Campaigns:', this.rejectedCampaigns);
      } catch (error) {
        console.error('Error fetching campaigns:', error.message);
      }
    },

    async fetchMessages(campaignId) {
      try {
        const token = localStorage.getItem('token');
        const response = await axios.get(`http://localhost:5000/messages/${campaignId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        this.messages = response.data;
      } catch (error) {
        console.error('Error fetching messages:', error);
      }
    },
    async sendMessage() {
      if (!this.chatMessage.trim()) return;

      try {
        const token = localStorage.getItem('token');
        await axios.post(
          'http://localhost:5000/messages_send',
          {
            campaign_id: this.currentCampaignId,
            text: this.chatMessage,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        );
        this.fetchMessages(this.currentCampaignId);
        this.chatMessage = '';
      } catch (error) {
        console.error('Error sending message:', error);
      }
    },
    logout() {
      localStorage.removeItem('token');
      this.$router.push('/');
    },
    async updateStatus(newStatus, campaign_id) {
      const token = localStorage.getItem('token'); // JWT token from localStorage

      if (!token) {
        console.error('User is not authenticated. No token found.');
        return;
      }

      try {
        // Make the POST request using axios with async/await
        const response = await axios.post(
          'http://localhost:5000/update_request_status',
          {
            campaign_id: campaign_id,
            status: newStatus,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`, // Include JWT token
            },
          }
        );

        // Handle the successful response
        if (response.data && response.status === 200) {
          this.status = newStatus; // Update the status locally
          console.log(response.data.message);
          window.location.reload();
        } else {
          console.warn('Unexpected response:', response);
        }
      } catch (error) {
        // Handle errors
        if (error.response) {
          // Server responded with a status code other than 2xx
          console.error('Server error:', error.response.data.error);
        } else if (error.request) {
          // Request was sent but no response received
          console.error('No response received:', error.request);
        } else {
          // Something else caused the error
          console.error('Error updating status:', error.message);
        }
      }
    }


  },
};
</script>

<style scoped>
@import '../styles/static/request_from_sponsor.css';
</style>
