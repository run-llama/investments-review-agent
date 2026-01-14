document
  .getElementById("submitBtn")
  .addEventListener("click", async function () {
    const fileInput = document.getElementById("fileInput");
    const fileType = document.querySelector(
      'input[name="fileType"]:checked',
    ).value;
    const file = fileInput.files[0];

    if (!file) {
      alert("Please select a file");
      return;
    }

    if (!fileType) {
      alert("Please select a file type");
      return;
    }

    const endpoint = "/" + fileType + "s";

    const formData = new FormData();
    formData.append("upload_file", file);

    try {
      this.classList.add("loading");
      this.disabled = true;

      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      // Check if request was successful
      if (!response.ok) {
        const detail = await response.text();
        document.getElementById("errorText").textContent = detail;
        document.getElementById("errorSection").classList.remove("hidden");
      }

      // Parse JSON response
      const result = await response.json();

      // Display result
      document.getElementById("resultText").textContent = result.final_result;
      document.getElementById("resultSection").classList.remove("hidden");
    } catch (error) {
      console.error("Upload error:", error);
      alert("Upload failed: " + error.message);
    } finally {
      // Remove loading state
      this.classList.remove("loading");
      this.disabled = false;
    }
  });
