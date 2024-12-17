<template>
    <div class="dashboard">
        <header>
            <h1>Influencer's Profile</h1>
            <nav>
                <router-link to="/iDash">Profile</router-link>
                <router-link to="/active-campaigns">Active Campaigns</router-link>
                <router-link to="/" @click="logout">Logout</router-link>
            </nav>
            <div class="search-bar">
                <input type="text" v-model="searchQuery" placeholder="Search campaign..." />
                <button @click="searchCampaigns">Search</button>
            </div>

        </header>

        <main>
            <section class="welcome">
                <h2>Welcome</h2>

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
                        <div v-if="campaign.doneMessage" class="success-message">
                            {{ campaign.doneMessage }}
                        </div>
                    </div>

                    <div class="campaign-actions">
                        <button @click="openRequestPopup(campaign.id)" class="request-btn" id="R">Request</button>
                        <button @click="deleteCampaign(campaign.id)" class="delete-btn" id="R">Delete</button>
                    </div>
                </div>
            </section>

            <!-- Popup for sending request -->
            <div v-if="showRequestPopup" class="popup">
                <div class="popup-content">
                    <h3>Send Request for Campaign</h3>
                    <label>Custom Charge Amount:</label>
                    <input type="number" v-model="customAmount" required />
                    <label>Message:</label>
                    <textarea v-model="customMessage" required></textarea>
                    <button id="R" @click="sendRequest">Send</button>
                    <button @click="closeRequestPopup">Cancel</button>
                </div>
            </div>
        </main>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    data() {
        return {
            userName: '',
            searchQuery: '',
            campaigns: [],
            showRequestPopup: false,
            selectedCampaignId: null,
            customAmount: '',
            customMessage: ''
        };
    },
    created() {
        this.fetchCampaigns();
    },
    methods: {
        async fetchCampaigns() {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://localhost:5000/all-campaigns', {
                    headers: {
                        Authorization: `Bearer ${token}`
                    }
                });
                this.campaigns = response.data.campaigns;
                console.log(response.data.campaigns);
                // Add `doneMessage` to each campaign initially as empty

            } catch (error) {
                console.error("Error fetching campaigns:", error);
                alert("Failed to fetch campaigns");
            }
        },

        async searchCampaigns() {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://localhost:5000/search-campaigns', {
                    headers: {
                        Authorization: `Bearer ${token}`,
                    },
                    params: {
                        title: this.searchQuery || '', // Default to empty string if searchQuery is not set
                        niche: this.searchQuery || '', // Same for niche
                    },
                });
                this.campaigns = response.data.campaigns;
            } catch (error) {
                console.error("Error searching campaigns:", error);
                alert("Failed to search campaigns");
            }
        },

        openRequestPopup(campaignId) {
            this.selectedCampaignId = campaignId;
            this.showRequestPopup = true;
        },
        closeRequestPopup() {
            this.showRequestPopup = false;
            this.customAmount = '';
            this.customMessage = '';
        },
        async sendRequest() {
            try {
                const token = localStorage.getItem('token');
                await axios.post(
                    `http://localhost:5000/adrequest`,
                    {
                        campaign_id: this.selectedCampaignId,
                        amount: this.customAmount,
                        message: this.customMessage
                    },
                    {
                        headers: { Authorization: `Bearer ${token}` }
                    }
                );

                // Find the specific campaign and set the success message
                const campaign = this.campaigns.find(c => c.id === this.selectedCampaignId);
                if (campaign) {
                    campaign.doneMessage = 'Request sent successfully!';
                }

                this.closeRequestPopup();
            } catch (error) {
                console.error("Error sending request:", error);
                alert("Failed to send request");
            }
        },
        deleteCampaign(id) {
            // Delete campaign logic here
        }
    }
};
</script>

<style scoped>
@import '../styles/static/sponsor.css';

.search-bar {
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 20px 0;
}

.search-bar input {
    width: 300px;
    padding: 10px 15px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 16px;
    outline: none;
    transition: all 0.3s ease;
}

.search-bar input:focus {
    border-color: #007BFF;
    box-shadow: 0 0 5px rgba(0, 123, 255, 0.5);
}

.search-bar button {
    margin-left: 10px;
    padding: 10px 20px;
    background-color: #007BFF;
    color: #fff;
    border: none;
    border-radius: 5px;
    font-size: 16px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.search-bar button:hover {
    background-color: #0056b3;
}


.welcome {
    padding-bottom: 100px;
}

#R {

    margin: 5px;
}

/* Popup Background Overlay */
.popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1000;
}

.success-message {
    color: green;
    font-weight: bold;
    margin-top: 10px;
}


/* Popup Content Box */
.popup-content {
    background: #fff;
    width: 400px;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    text-align: center;
}

/* Popup Header */
.popup-content h3 {
    margin: 0 0 15px;
    font-size: 1.5em;
    color: #333;
}

/* Input and Textarea Fields */
.popup-content label {
    display: block;
    font-weight: bold;
    margin-top: 10px;
    color: #666;
}

.success-message {
    margin-top: 15px;
    color: #4CAF50;
    font-weight: bold;
    font-size: 1em;
}

.popup-content input[type="number"],
.popup-content textarea {
    width: 100%;
    padding: 10px;
    margin-top: 5px;
    border: 1px solid #ccc;
    border-radius: 5px;
    font-size: 1em;
}

/* Buttons */
.popup-content button {
    margin-top: 15px;
    padding: 10px 20px;
    border: none;
    border-radius: 5px;
    font-size: 1em;
    cursor: pointer;
}

.popup-content button:first-child {
    background-color: #4CAF50;
    /* Send button color */
    color: white;
    margin-right: 10px;
}

/* Buttons with spacing */
.popup-buttons {
    display: flex;
    justify-content: space-between;
    margin-top: 15px;
}

.popup-content button:last-child {
    background-color: #f44336;
    /* Cancel button color */
    color: white;
}

/* Responsive adjustments */
@media (max-width: 480px) {
    .popup-content {
        width: 90%;
    }
}



/* Additional styles for the sponsor dashboard */
</style>

<style>
@import '../styles/static/influ_profile.css';

/* Additional styles for error message */
.error-message {
    color: red;
    margin-top: 10px;
}
</style>
