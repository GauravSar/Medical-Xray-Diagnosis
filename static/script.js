function toggleDarkMode() {
    document.body.classList.toggle("dark");
}

async function predict() {
    const fileInput = document.getElementById("imageInput");
    const previewImage = document.getElementById("previewImage");
    const resultBox = document.getElementById("result");
    const riskBadge = document.getElementById("riskBadge");
    const progressFill = document.getElementById("progressFill");
    const confidenceText = document.getElementById("confidenceText");

    if (!fileInput.files.length) {
        alert("Please upload an image");
        return;
    }

    const file = fileInput.files[0];
    previewImage.src = URL.createObjectURL(file);
    previewImage.style.display = "block";

    const formData = new FormData();
    formData.append("file", file);

    resultBox.classList.remove("hidden");
    riskBadge.innerText = "Analyzing...";

    const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    const confidence = data.confidence_percent;

    /* Risk logic */
    let riskClass = "";
    let riskText = "";

    if (confidence < 50) {
        riskClass = "risk-normal";
        riskText = "🟢 Normal Risk";
    } else if (confidence < 75) {
        riskClass = "risk-moderate";
        riskText = "🟡 Moderate Risk";
    } else {
        riskClass = "risk-high";
        riskText = "🔴 High Risk";
    }

    riskBadge.className = `risk-badge ${riskClass}`;
    riskBadge.innerText = `${riskText} — ${data.prediction}`;

    progressFill.style.width = confidence + "%";
    confidenceText.innerText = confidence + "%";
}
