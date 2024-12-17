<template>
  <div class="login-container">
    <form @submit.prevent="loginUser">
      <h2>User Login or Admin Login</h2>

      <div class="form-group">
        <label for="username">Username</label>
        <input
          type="text"
          id="username"
          v-model="username"
          placeholder="Enter Username"
          required
        />
      </div>

      <div class="form-group">
        <label for="password">Password</label>
        <input
          type="password"
          id="password"
          v-model="password"
          placeholder="Enter Password"
          required
        />
      </div>

      <button type="submit">Login</button>

      <p id="R"><b>Influencer signUp?</b></p>
      <a id="R" href="/UserRegister">Sign Up</a>

      <p id="R"><b>Sponsor signUp?</b></p>
      <a id="R" href="/Sponsorsignup">Sign Up</a>

      <p v-if="errorMessage" id="R" class="error-message">{{ errorMessage }}</p>
    </form>

    <!-- Popup for special messages -->
    <div v-if="popupMessage" class="popup-overlay">
      <div class="popup">
        <p>{{ popupMessage }}</p>
        <button @click="closePopup">OK</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      errorMessage: '',
      popupMessage: '' // To store popup messages
    };
  },
  methods: {
    async loginUser() {
      try {
        const response = await axios.post('http://127.0.0.1:5000/', {
          username: this.username,
          password: this.password
        });

        // Clear any previous error or popup message
        this.errorMessage = '';
        this.popupMessage = '';

        if (response.status === 200 && response.data.access_token) {
          // Store the JWT token in localStorage
          localStorage.setItem('token', response.data.access_token);

          // Check role and redirect accordingly
          const userRole = response.data.role;
          if (userRole === 'admin') {
            this.$router.push('/admin');
          } else if (userRole === 'sponsor') {
            this.$router.push('/sponsor-home');
          } else if (userRole === 'influencer') {
            this.$router.push('/iDash');
          } else {
            this.$router.push('/campain');
          }
        }
      } catch (error) {
        const errorMessage = error.response?.data?.message;

        // Trigger specific messages based on server response
        if (errorMessage === "User is flagged by admin, access restricted.") {
          this.popupMessage = "Your account has been flagged by the admin. Please contact support.";
        } else if (errorMessage === "Your account is under verification. Please contact support for more information.") {
          this.popupMessage = "Your account is under verification. Please wait or contact support.";
        } else {
          this.errorMessage = errorMessage || "An error occurred. Please try again.";
        }
      }
    },
    closePopup() {
      this.popupMessage = ''; // Close the popup
    }
  }
};
</script>


<style>
@import '../styles/static/style.css';

/* Popup styling */
.popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.popup {
  background: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}

.popup button {
  margin-top: 10px;
  padding: 8px 16px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.popup button:hover {
  background-color: #0056b3;
}

</style>

