<template>
  <div class="signin-container register">
    <h2>Influencer Registration</h2>
    <form @submit.prevent="registerUser" class="signin-form">
      <!-- Username Field -->
      <div class="input-group">
        <label for="username">Username:</label>
        <input type="text" id="username" v-model="username" placeholder="Enter your username" required />
      </div>

      <div class="input-group">
        <label for="username">gmail:</label>
        <input type="text" id="username" v-model="gmail" placeholder="Enter your gmail" required />
      </div>

      <!-- Category Field -->
      <div class="input-group">
        <label for="category">Category:</label>
        <input type="text" id="category" v-model="category" placeholder="Enter your category" required />
      </div>

      <!-- Niche Field -->
      <div class="input-group">
        <label for="niche">Niche:</label>
        <input type="text" id="niche" v-model="niche" placeholder="Enter your niche" required />
      </div>

      <!-- Reach Field -->
      <div class="input-group">
        <label for="reach">Reach:</label>
        <input type="number" id="reach" v-model="reach" placeholder="Enter your reach" required />
      </div>

      <!-- Password Field -->
      <div class="input-group">
        <label for="password">Password:</label>
        <input type="password" id="password" v-model="password" placeholder="Enter your password" required />
      </div>

      <!-- Confirm Password Field -->
      <div class="input-group">
        <label for="confirmPassword">Confirm Password:</label>
        <input type="password" id="confirmPassword" v-model="confirmPassword" placeholder="Confirm your password" required />
      </div>

      <!-- Submit Button -->
      <button type="submit" class="signin-btn">Sign Up</button>
    </form>

    <!-- Display Message -->
    <p v-if="message" :class="{ 'error-message': isError, 'success-message': !isError }">{{ message }}</p>
    <p>Already have an account? <a href="/">Login here</a></p>
  </div>
</template>
<script>
import axios from 'axios';

export default {
  data() {  
    return {
      username: '',
      gmail:'',
      category: '',
      niche: '',
      reach: null,
      password: '',
      confirmPassword: '',
      message: '',
      isError: false,
    };
  },
  methods: {
    async registerUser() {
      // Clear previous messages
      this.message = 'Submitting...';
      this.isError = false;

      // Basic password validation
      if (this.password !== this.confirmPassword) {
        this.message = 'Passwords do not match.';
        this.isError = true;
        return;
      }

      // Input validation
      if (this.reach <= 0) {
        this.message = 'Reach must be a positive number.';
        this.isError = true;
        return;
      }

      // Make API call to register the user
      try {
        const response = await axios.post('http://127.0.0.1:5000/register', {
          username: this.username,
          gmail:this.gmail,
          category: this.category,
          niche: this.niche,
          reach: this.reach,
          password: this.password,
          role: 'influencer',
        });

        // Display a custom success message
        this.message = 'Signup successfully!';
        console.log(this.message);
        this.isError = false;

        // Clear form fields
        this.username = '';
        this.gmail = '';
        this.category = '';
        this.niche = '';
        this.reach = null;
        this.password = '';
        this.confirmPassword = '';
      } catch (error) {
        console.error('Registration error:', error);
        this.isError = true;

        // Handle error response
        if (error.response) {
          if (error.response.status === 409) {
            this.message = 'User already exists. Please choose a different username.';
          } else {
            this.message = error.response.data.message || 'An error occurred. Please try again.';
          }
        } else if (error.request) {
          this.message = 'No response received. Please check your connection and try again.';
        } else {
          this.message = 'An unexpected error occurred. Please try again.';
        }
      }
    },
  },
};
</script>


<style>
@import '../styles/static/sign.css';

/* Additional styles for success and error messages */
.error-message {
  color: red;
}

.success-message {
  color: green;
}
</style>
