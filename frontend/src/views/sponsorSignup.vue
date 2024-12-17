<template>
  <div id = "R" class="signin-container">
    <form @submit.prevent="signupUser" class="signin-form">
      <h2 id = "k">{{ title }}</h2>

      <div class="input-group">
        <label for="username">Username</label>
        <input type="text" v-model="username" id="username" name="username" required />
      </div>

      <div class="input-group">
        <label for="username">gmail:</label>
        <input type="text" id="username" v-model="gmail" required />
      </div>

      <div class="input-group">
        <label for="companyName">Company Name / Individual Name</label>
        <input type="text" v-model="companyName" id="companyName" name="companyName" required />
      </div>

      <div class="input-group">
        <label for="industry">Industry</label>
        <input type="text" v-model="industry" id="industry" name="industry" required />
      </div>

      <div class="input-group">
        <label for="budget">Budget</label>
        <input type="number" v-model="budget" id="budget" name="budget" required />
      </div>

      <div class="input-group">
        <label for="password">Password</label>
        <input type="password" v-model="password" id="password" name="password" required />
      </div>
      
      <div class="input-group">
        <label for="conformpass">Confirm Password</label>
        <input type="password" v-model="confirmPassword" id="conformpass" name="confirmpass" required />
      </div>

      <button id="R" type="submit" class="signin-btn">Sign Up</button>
    </form>

    <!-- Show success message on successful signup -->
    <p v-if="successMessage" style="color: green;">{{ successMessage }}</p>
    
    <!-- Show error message -->
    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>

    <p id="R">Already have an account? <a href="/">Login here</a></p>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      title: "Sponsor Signup",
      username: "",
      gmail:"",
      password: "",
      confirmPassword: "",
      companyName: "",
      industry: "",
      budget: "",
      errorMessage: "",
      successMessage: "",
    };
  },
  methods: {
    async signupUser() {
      this.errorMessage = "";
      this.successMessage = "";

      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match!";
        return;
      }

      try {
        const response = await axios.post("http://127.0.0.1:5000/sponsorsignup", {
          username: this.username,
          gmail:this.gmail,
          password: this.password,
          role: "sponsor",
          companyName: this.companyName,
          industry: this.industry,
          budget: this.budget,
        });
        console.log(this.response)

        if (response.status === 201) {  
          this.successMessage = "Signup successful! Redirecting to login...";
          setTimeout(() => {
            this.$router.push("/");
          }, 2000);
        }
      } catch (error) {
        this.errorMessage = error.response?.data?.message || "An error occurred. Please try again.";
        console.error("Signup error:", this.errorMessage);
      }
    },
  },
};
</script>


<style scoped>

#R{
  padding-top:0px;
  padding-bottom: 10px;
}

</style>


