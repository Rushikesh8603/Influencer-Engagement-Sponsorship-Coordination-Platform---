<template>
    <div>
      <button @click="triggerExport">Export Campaigns as CSV</button>
      <div v-if="status === 'pending'">Export in progress...</div>
      <div v-if="status === 'completed'">
        Export completed. <a :href="filePath" download>Download CSV</a>

      </div>
      <div v-if="status === 'error'">{{ errorMessage }}</div>
    </div>
  </template>
  
  <script>
  import axios from "axios";
  
  export default {
    data() {
      return {
        status: "",
        filePath: "",
        errorMessage: "",
        taskId: null,
      };
    },
    methods: {
      async triggerExport() {
        try {
          const token = localStorage.getItem("token"); // Retrieve the token from storage
          const response = await axios.post(
            "http://localhost:5000/trigger-export", // Full URL here
            {}, // Request body, empty for this example
            {
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`, // Send the token in the Authorization header
              },
            }
          );
  
          const data = response.data;
          console.log(data); // Log the response to verify structure
          if (data.status === "success") {
            this.taskId = data.task_id;
            this.checkStatus();
          } else {
            this.errorMessage = data.message;
          }
        } catch (error) {
          this.errorMessage = "Failed to trigger export.";
        }
      },
      async checkStatus() {
        if (!this.taskId) return;
  
        const interval = setInterval(async () => {
          try {
            const response = await axios.get(
              `http://localhost:5000/check-task-status/${this.taskId}` // Full URL here
            );
            const data = response.data;
            console.log("Task Status Response:", data);
            this.status = data.status;
  
            if (data.status === "completed") {
              clearInterval(interval);
              this.filePath = `http://127.0.0.1:5000/${data.file_path}`;

            } else if (data.status === "error") {
              clearInterval(interval);
              this.errorMessage = data.message;
            }
          } catch (error) {
            clearInterval(interval);
            this.errorMessage = "Failed to fetch task status.";
          }
        }, 2000); // Poll every 2 seconds
      },
    },
  };
  </script>
  