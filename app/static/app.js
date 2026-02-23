const form = document.getElementById("upload-form");
const fileInput = document.getElementById("file-input");
const statusEl = document.getElementById("status");
const result = document.getElementById("result");

const setText = (id, value) => {
  document.getElementById(id).textContent = value;
};

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  result.classList.add("hidden");

  const file = fileInput.files[0];
  if (!file) {
    statusEl.textContent = "Please select a file.";
    return;
  }

  statusEl.textContent = "Processing...";

  const formData = new FormData();
  formData.append("file", file);

  try {
    const uploadResponse = await fetch("/api/images", {
      method: "POST",
      body: formData,
    });

    const uploadJson = await uploadResponse.json();
    if (!uploadResponse.ok) {
      statusEl.textContent = uploadJson.detail || "Upload failed.";
      return;
    }

    const imageId = uploadJson.data.image_id;
    const detailResponse = await fetch(`/api/images/${imageId}`);
    const detailJson = await detailResponse.json();

    if (!detailResponse.ok || detailJson.status !== "success") {
      statusEl.textContent = detailJson.error || "Processing failed.";
      return;
    }

    const data = detailJson.data;
    setText("original-name", data.original_name);
    setText("caption", data.caption || "Caption unavailable");
    setText("meta-width", data.metadata.width);
    setText("meta-height", data.metadata.height);
    setText("meta-format", data.metadata.format);
    setText("meta-size", data.metadata.size_bytes);

    document.getElementById("thumb-small").src = data.thumbnails.small;
    document.getElementById("thumb-medium").src = data.thumbnails.medium;

    result.classList.remove("hidden");
    statusEl.textContent = "Done.";
  } catch (error) {
    statusEl.textContent = "Unexpected error while processing image.";
  }
});
