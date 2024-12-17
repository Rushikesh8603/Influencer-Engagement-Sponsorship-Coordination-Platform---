<template>
    <div class="dashboard">
        <header>
            <h1>Sponsor Dashboard</h1>
            <nav>
                <router-link to="/sponsor-home">Profile</router-link>
                <router-link to="/campaign">Campaigns</router-link>
                <router-link to="/influencer_requests">Requested</router-link>

                <router-link to="/">Logout</router-link>
            </nav>
        </header>

        <main>
            <section class="welcome">
                <h2>Welcome (❁´◡`❁)</h2>

                <!-- Pending Campaigns -->
                <h2 style="color: orange;">Pending</h2>
                <div v-if="pendingCampaigns.length === 0">
                    <p>No pending campaigns.</p>
                </div>
                <div v-for="campaign in pendingCampaigns" :key="campaign.id" class="campaign">
                    <div class="campaign-details">
                        <div v-if="campaign.doneMessage" class="success-message">{{ campaign.doneMessage }}</div>
                        <div class="detail"><span class="label">Title:</span> <span>{{ campaign.title }}</span></div>
                        <div class="detail"><span class="label">Description:</span> <span>{{ campaign.description
                                }}</span></div>
                        <div class="detail"><span class="label">Niche:</span> <span>{{ campaign.niche }}</span></div>
                        <div class="detail"><span class="label">Start Date:</span> <span>{{ campaign.start_date
                                }}</span></div>
                        <div class="detail"><span class="label">End Date:</span> <span>{{ campaign.end_date }}</span>
                        </div>
                        <div class="detail"><span class="label">Budget:</span> <span>{{ campaign.budget }}</span></div>
                        <div class="detail"><span class="label">Visibility:</span> <span>{{ campaign.visibility
                                }}</span></div>
                    </div>
                    <div class="campaign-actions">
                        <button id = "k" @click="openRequestPopup(campaign)" class="accept-btn">Accept</button>
                        <button id = "kk" @click="rejectRequest(campaign.id)" class="reject-btn">Reject</button>
                    </div>
                </div>

                <!-- Accepted Campaigns -->
                <h2 style="color: green;">Accepted</h2>
                <div v-if="acceptedCampaigns.length === 0">
                    <p>No accepted campaigns.</p>
                </div>
                <div v-for="campaign in acceptedCampaigns" :key="campaign.id" class="campaign">
                    <div class="campaign-details">
                        <div v-if="campaign.doneMessage" class="success-message">{{ campaign.doneMessage }}</div>
                        <div class="detail"><span class="label">Title:</span> <span>{{ campaign.title }}</span></div>
                        <div class="detail"><span class="label">Description:</span> <span>{{ campaign.description
                                }}</span></div>
                        <div class="detail"><span class="label">Niche:</span> <span>{{ campaign.niche }}</span></div>
                        <div class="detail"><span class="label">Start Date:</span> <span>{{ campaign.start_date
                                }}</span></div>
                        <div class="detail"><span class="label">End Date:</span> <span>{{ campaign.end_date }}</span>
                        </div>
                        <div class="detail"><span class="label">Budget:</span> <span>{{ campaign.budget }}</span></div>
                        <div class="detail"><span class="label">Visibility:</span> <span>{{ campaign.visibility
                                }}</span></div>
                    </div>
                </div>

                <!-- Rejected Campaigns -->
                <h2 style="color: red;">Rejected</h2>
                <div v-if="rejectedCampaigns.length === 0">
                    <p>No rejected campaigns.</p>
                </div>
                <div v-for="campaign in rejectedCampaigns" :key="campaign.id" class="campaign">
                    <div class="campaign-details">
                        <div v-if="campaign.doneMessage" class="success-message">{{ campaign.doneMessage }}</div>
                        <div class="detail"><span class="label">Title:</span> <span>{{ campaign.title }}</span></div>
                        <div class="detail"><span class="label">Description:</span> <span>{{ campaign.description
                                }}</span></div>
                        <div class="detail"><span class="label">Niche:</span> <span>{{ campaign.niche }}</span></div>
                        <div class="detail"><span class="label">Start Date:</span> <span>{{ campaign.start_date
                                }}</span></div>
                        <div class="detail"><span class="label">End Date:</span> <span>{{ campaign.end_date }}</span>
                        </div>
                        <div class="detail"><span class="label">Budget:</span> <span>{{ campaign.budget }}</span></div>
                        <div class="detail"><span class="label">Visibility:</span> <span>{{ campaign.visibility
                                }}</span></div>
                    </div>
                </div>
            </section>
        </main>

        <!-- Popup for Accepting Influencer's Request -->
        <div v-if="showRequestPopup" class="popup-overlay">
            <div class="popup-content">
                <h3  id = "R" style="color: blue;">Influencer Request and Negotiation</h3>
                <p id = 'R'><strong>Influencer Name:</strong> {{ selectedCampaign.influencer_name }}</p>
                <p id = "R"><strong>Amount Requested:</strong> {{ selectedCampaign.amount }}</p>
                <p id = "R"><strong>Message:</strong> {{ selectedCampaign.message }}</p>
                <button id = 'R' @click="confirmAcceptance(selectedCampaign.id)" class="accept-btn">Confirm Accept</button>
                <button id = "R" @click="closeRequestPopup" class="close-btn">Close</button>
            </div>
        </div>
    </div>
</template>


<script>
import axios from 'axios';

export default {
    data() {
        return {
            searchQuery: '',
            campaigns: [],
            showRequestPopup: false,
            selectedCampaign: null,
        };
    },
    computed: {
        pendingCampaigns() {
            
            const pending = this.campaigns.filter(campaign => campaign.status === 'pending');
            console.log(this.campaigns);
            return pending;
        },
        acceptedCampaigns() {
            const accepted = this.campaigns.filter(campaign => campaign.status === 'Accepted');
            console.log("Accepted Campaigns:", accepted); // Check for updates
            return accepted;
        },
        rejectedCampaigns() {
            const rejected = this.campaigns.filter(campaign => campaign.status === 'Rejected');
            console.log("Rejected Campaigns:", rejected); // Check for updates
            return rejected;
        }
    },

    created() {
        this.fetchCampaigns();
    },
    methods: {
        async fetchCampaigns() {
            try {
                const token = localStorage.getItem('token');
                const response = await axios.get('http://localhost:5000/all-requested-campaigns', {
                    headers: { Authorization: `Bearer ${token}` }
                });
                this.campaigns = response.data.campaigns.map(campaign => ({
                    ...campaign,
                    influencer_name: campaign.influencer_name,
                    amount: campaign.requested_amount,
                    message: campaign.message
                }));

                console.log(response.data.campaigns)

            } catch (error) {
                console.error("Error fetching campaigns:", error);
                alert("Failed to fetch campaigns");
            }
        },
        openRequestPopup(campaign) {
            this.selectedCampaign = campaign;
            this.showRequestPopup = true;
        },
        closeRequestPopup() {
            this.showRequestPopup = false;
            this.selectedCampaign = null;
        },
        async confirmAcceptance(campaignId) {
            try {
                const token = localStorage.getItem('token');
                await axios.post(`http://localhost:5000/accept-request/${campaignId}`, {}, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                alert("Request accepted successfully!");
                this.closeRequestPopup();
                await new Promise(resolve => setTimeout(resolve, 5000));
                this.fetchCampaigns();
            } catch (error) {
                console.error("Error accepting request:", error);
                alert("Failed to accept request");
            }
        },
        async rejectRequest(campaignId) {
            try {
                const token = localStorage.getItem('token');
                await axios.delete(`http://localhost:5000/reject-request/${campaignId}`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                alert("Request rejected successfully!");
                this.fetchCampaigns();
            } catch (error) {
                console.error("Error rejecting request:", error);
                alert("Failed to reject request");
            }
        }
    }
};
</script>


<style scoped>
@import '../styles/static/sponsor.css';

.welcome {
    padding-bottom: 100px;
}

#R {
    margin: 10px;
 
    padding: 5px;
}

#k {
    margin: 20px;
    color: red;
    background-color:greenyellow;
}
#kk {
    margin: 20px;
    
    background-color: red;
}

/* Popup styles */
.popup-overlay {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    transition: opacity 0.5s ease, visibility 0.5s ease;
}

.popup-content {
    background: white;
    padding: 50px;
    border-radius: 5px;
    width: 300px;
    text-align: center;
}

.close-btn,
.accept-btn {
    margin: 10px;
    padding: 8px 16px;
    cursor: pointer;
}

.close-btn {
    background-color: rgb(239, 9, 39);
    width: 130px;

}
</style>
