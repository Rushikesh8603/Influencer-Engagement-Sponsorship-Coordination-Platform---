<template>
  <div class="full-screen-overlay">
    <h1 id="R">Search for Influencers</h1>
    <div class="navbar">
      <div class="search-container">
        <form @submit.prevent role="search">
          <input type="search" v-model="searchQuery" placeholder="Search..." required class="search-input" />
          <button type="submit" class="search-button">🔍</button>
        </form>
      </div>

      <!-- Category Dropdown -->
      <div class="dropdown">
        <button class="dropdown-button">{{ selectedCategory || "Select Category" }}</button>
        <div class="dropdown-content">
          <a href="#" @click.prevent="selectCategory('Technology')">Technology</a>
          <a href="#" @click.prevent="selectCategory('Health')">Health</a>
          <a href="#" @click.prevent="selectCategory('Fashion')">Fashion</a>
          <a href="#" @click.prevent="selectCategory('Food')">Food</a>
        </div>
      </div>

      <!-- Followers Dropdown -->
      <div class="dropdown">
        <button class="dropdown-button">{{ selectedFollowers || "Select Followers" }}</button>
        <div class="dropdown-content">
          <a href="#" @click.prevent="selectFollowers('1k-10k')">1k-10k</a>
          <a href="#" @click.prevent="selectFollowers('10k-100k')">10k-100k</a>
          <a href="#" @click.prevent="selectFollowers('100k-500k')">100k-500k</a>
          <a href="#" @click.prevent="selectFollowers('500k+')">500k+</a>
        </div>
      </div>
      <router-link style="padding: 80px; color: black; font-weight:900;" to="/sponsor-home">Profile</router-link>
      <router-link style="font-weight: 900; color: black;" to="/campaign">Campaigns</router-link>
    </div>
    <div class="scroll-container">
      <main>
        <!-- Pending Influencers -->
        <section class="rushi">
          <!-- Pending Influencers -->
          <h1 class="section-heading">Pending Influencers</h1>
          <div class="influencer-row-scroll">
            <div v-if="pendingInfluencers.length > 0" class="influencer-row">
              <div v-for="influencer in pendingInfluencers" :key="influencer.id" class="profile-card">
                <h3 class="profile-name">{{ influencer.username }}</h3>
                <p class="profile-role">{{ influencer.role }}</p>
                <div class="profile-details">
                  <div class="detail">
                    <span class="detail-title">Category:</span>
                    <span class="detail-value">{{ influencer.category }}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-title">Niche:</span>
                    <span class="detail-value">{{ influencer.niche }}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-title">Reach:</span>
                    <span class="detail-value">{{ influencer.reach }}K</span>
                  </div>
                  <button @click="openChat(influencer.id)" class="request-button">Request</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Accepted Influencers -->
          <h2 class="section-heading">Accepted Influencers</h2>
          <div class="influencer-row-scroll">
            <div v-if="acceptedInfluencers.length > 0" class="influencer-row">
              <div v-for="influencer in acceptedInfluencers" :key="influencer.id" class="profile-card">
                <h3 class="profile-name">{{ influencer.username }}</h3>
                <p class="profile-role">{{ influencer.role }}</p>
                <div class="profile-details">
                  <div class="detail">
                    <span class="detail-title">Category:</span>
                    <span class="detail-value">{{ influencer.category }}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-title">Niche:</span>
                    <span class="detail-value">{{ influencer.niche }}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-title">Reach:</span>
                    <span class="detail-value">{{ influencer.reach }}K</span>
                  </div>
                  <button @click="openChat(influencer.id)" class="request-button">Request</button>
                </div>
              </div>
            </div>
          </div>

          <!-- Rejected Influencers -->
          <h2 class="section-heading">Rejected Influencers</h2>
          <div class="influencer-row-scroll">
            <div v-if="rejectedInfluencers.length > 0" class="influencer-row">
              <div v-for="influencer in rejectedInfluencers" :key="influencer.id" class="profile-card">
                <h3 class="profile-name">{{ influencer.username }}</h3>
                <p class="profile-role">{{ influencer.role }}</p>
                <div class="profile-details">
                  <div class="detail">
                    <span class="detail-title">Category:</span>
                    <span class="detail-value">{{ influencer.category }}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-title">Niche:</span>
                    <span class="detail-value">{{ influencer.niche }}</span>
                  </div>
                  <div class="detail">
                    <span class="detail-title">Reach:</span>
                    <span class="detail-value">{{ influencer.reach }}K</span>
                  </div>
                  <button @click="openChat(influencer.id)" class="request-button">Request</button>
                </div>
              </div>
            </div>
          </div>
        </section>


        <div v-if="isChatOpen" class="chatbox">
          <div class="chat-header">
            <h3>Chat with Influencer</h3>
            <button @click="closeChat" class="close-chat-btn">X</button>
          </div>
          <div class="chat-messages">
            <div v-for="message in messages" :key="message.id" class="chat-message">

              <div
                :class="{ 'sender-message': message.sender === 'sponsor', 'influencer-message': message.sender === 'influencer' }">
                <strong>{{ message.sender === 'sponsor' ? 'Sponsor:' : 'influencer:' }}</strong> {{ message.text }}
              </div>
            </div>
          </div>
          <div class="chat-input-container">
            <textarea v-model="chatMessage" placeholder="Type your message..." rows="3"></textarea>
            <button @click="sendMessage" class="send-btn">Send</button>
          </div>
        </div>
      </main>
    </div>
  </div>
</template>

<script>
import axios from "axios";


export default {
  data() {
    return {
      pendingInfluencers: [],  // Store pending influencers
      acceptedInfluencers: [], // Store accepted influencers
      rejectedInfluencers: [], // Store rejected influencers
      searchQuery: "",
      selectedCategory: null,
      selectedFollowers: null,
      influencers: [], // Store search results here
      isChatOpen: false,
      currentChatInfluencerId: null,
      chatMessage: "",
      messages: [],
    };
  },
  computed: {
    filteredInfluencers() {
      // Show all influencers if no filters are applied
      if (!this.searchQuery && !this.selectedCategory && !this.selectedFollowers) {
        return this.influencers;
      }
      // Filter influencers based on the search query and selected filters
      return this.influencers.filter((influencer) => {
        const matchesQuery = influencer.username
          .toLowerCase()
          .startsWith(this.searchQuery.toLowerCase());
        const matchesCategory = this.selectedCategory
          ? influencer.category === this.selectedCategory
          : true;
        const matchesFollowers = this.selectedFollowers
          ? influencer.reach >= this.getFollowerRange(this.selectedFollowers).min &&
          influencer.reach <= this.getFollowerRange(this.selectedFollowers).max
          : true;
        return matchesQuery && matchesCategory && matchesFollowers;
      });
    },
  },
  watch: {
    searchQuery: "performSearch",
    selectedCategory: "performSearch",
    selectedFollowers: "performSearch",
  },
  methods: {
    async performSearch() {
      try {
        const response = await axios.get("http://localhost:5000/search_influencers", {
          params: {
            query: this.searchQuery,
            category: this.selectedCategory,
            followers: this.selectedFollowers,
            campain_id: this.$route.params.id,  // Ensure this is the correct ID from the route params
          },
        });

        // Store the separate influencer lists in their respective properties
        this.pendingInfluencers = response.data.pending;
        this.acceptedInfluencers = response.data.accepted;
        this.rejectedInfluencers = response.data.rejected;
        console.log(this.pendingInfluencers)
        console.log(this.acceptedInfluencers)
        console.log(this.rejectedInfluencers)
      } catch (error) {
        console.error("Error fetching influencer data:", error);
        this.errorMessage = "An error occurred while fetching data.";
      }
    },


    selectCategory(category) {
      this.selectedCategory = category;
    },
    selectFollowers(followersRange) {
      this.selectedFollowers = followersRange;
    },
    getFollowerRange(range) {
      const ranges = {
        "1k-10k": { min: 1, max: 10 },
        "10k-100k": { min: 10, max: 100 },
        "100k-500k": { min: 100, max: 500 },
        "500k+": { min: 500, max: Infinity },
      };
      return ranges[range] || { min: 0, max: Infinity };
    },
    closeChat() {
      this.isChatOpen = false;
      this.currentChatInfluencerId = null;
      this.messages = [];
    },
    openChat(influencerId) {
      this.currentChatInfluencerId = influencerId;
      console.log(this.currentChatInfluencerId);

      this.isChatOpen = true;
      this.fetchMessages();

      fetch('http://localhost:5000/trigger-reminder', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then(response => {
          if (response.ok) {
            console.log("Reminder task triggered successfully.");
          } else {
            console.error("Failed to trigger reminder task.");
          }
        })
        .catch(error => {
          console.error("Error:", error);
        });
    },
    sendMessage() {
      if (!this.chatMessage.trim()) return;

      const message = {
        id: Date.now(),
        sender: 'sponsor',
        text: this.chatMessage,
      };


      this.messages.push(message);  // Add message to the local chat
      console.log(this.messages);
      this.chatMessage = "";  // Clear chat input

      const token = localStorage.getItem('token');  // Get the JWT token from localStorage

      // Send the message to the backend (this could be saved in a DB)
      axios.post("http://localhost:5000/send_message", {
        influencerId: this.currentChatInfluencerId,
        message,
        ampain_id: this.$route.params.id
      }, {
        headers: {
          Authorization: `Bearer ${token}`,  // Include the token in the Authorization header
        },
      })
        .then(response => {
          console.log("Message sent", response);
        })
        .catch(error => {
          console.error("Error sending message:", error);
        });
    },
    async fetchMessages() {
      if (!this.currentChatInfluencerId) {
        console.warn('Chat Influencer ID is not set.');
        return;
      }

      const token = localStorage.getItem('token'); // JWT token
      if (!token) {
        console.error('User is not authenticated.');
        return;
      }

      const campaignId = this.$route.params.id;

      try {
        // Step 1: Create or validate the status entry
        const createStatusResponse = await axios.post(
          'http://localhost:5000/create_status',
          {
            campaign_id: campaignId,
            receiver_id: this.currentChatInfluencerId,
          },
          {
            headers: {
              Authorization: `Bearer ${token}`, // Include the JWT token
            },
          }
        );
        console.log('Status created or validated:', createStatusResponse.data);

        // Step 2: Fetch messages after successful status validation
        const messagesResponse = await axios.get(
          `http://localhost:5000/get_messages/${this.currentChatInfluencerId}`,
          {
            headers: {
              Authorization: `Bearer ${token}`, // Include the JWT token
            },
            params: {
              campaign_id: campaignId, // Pass the campaign ID as a query parameter
            },
          }
        );

        this.messages = messagesResponse.data; // Set the messages in the frontend
        console.log('Fetched messages:', this.messages);
      } catch (error) {
        if (error.response) {
          // Server responded with an error
          console.error('Error:', error.response.data);
        } else if (error.request) {
          // Request was sent but no response received
          console.error('No response received:', error.request);
        } else {
          // Other errors
          console.error('Error:', error.message);
        }
      }
    }

  },
  mounted() {
    this.performSearch(); // Initial load to fetch all influencers
    // setInterval(this.fetchMessages, 5000); // Periodically fetch new messages
  },
};
</script>

<style scoped>
@import '../styles/static/search_influ.css';





/*  */
strong {
  font-weight: bold;
  margin-right: 5px;
}

.profile-card {
  position: relative;
  margin-bottom: 20px;
}

.chatbox {
  position: fixed;
  right: 0;
  top: 0;
  width: 300px;
  height: 80vh;
  background-color: #f9f9f9;
  border-left: 1px solid #ddd;
  display: flex;
  flex-direction: column;
  border-radius: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);

  background-size: cover;
  background-repeat: no-repeat;
  background-position: center;
  overflow: hidden;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: bold;
  background-color: #075E54;
  color: white;
  padding: 10px;
  border-top-left-radius: 20px;
  border-top-right-radius: 20px;
}

.close-chat-btn {
  cursor: pointer;
  background-color: #FF3B30;
  color: white;
  border: none;
  padding: 5px;
  border-radius: 5px;
}

.chat-messages {
  flex-grow: 1;
  overflow-y: auto;
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  scroll-behavior: smooth;
}

.chat-message {
  margin-bottom: 10px;
  max-width: 80%;
}

.sender-message {
  background-color: #DCF8C6;
  padding: 8px 12px;
  border-radius: 8px;
  text-align: left;
  align-self: flex-start;
}

.influencer-message {
  background-color: #ECE5DD;
  padding: 8px 12px;
  border-radius: 8px;
  text-align: left;
  align-self: flex-end;
}

.chat-input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f0f0f0;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  box-sizing: border-box;
}

.chat-input-container textarea {
  flex-grow: 1;
  resize: none;
  padding: 8px;
  border-radius: 5px;
  border: 1px solid #ddd;
  margin-right: 5px;
  height: 40px;
  max-height: 40px;
  /* Ensures a fixed height */
  overflow: hidden;
}

.send-btn {
  background-color: #075E54;
  color: white;
  border: none;
  border-radius: 5px;
  padding: 8px 12px;
  cursor: pointer;
}

.send-btn:hover {
  background-color: #128C7E;
}

/* Ensure non-scalable chat messages for consistent appearance */
.chatbox,
.chat-messages,
.chat-input-container,
.chat-message,
.send-btn,
.chat-input-container textarea {
  max-width: 100%;
  overflow: hidden;
}





/* extra scrool bar */


.chat-messages {
  flex-grow: 1;
  /* Allows it to expand and fill available space */
  overflow-y: auto;
  /* Enables vertical scrolling */
  padding: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  scroll-behavior: smooth;
  /* Smooth scrolling */
  max-height: calc(80vh - 120px);
  /* Adjust the height dynamically based on header and input */
}

.chat-input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f0f0f0;
  border-bottom-left-radius: 20px;
  border-bottom-right-radius: 20px;
  box-sizing: border-box;
}
</style>
