document.getElementById("submitBtn").addEventListener("click", async () => {
  const county = document.getElementById("cityInput").value;   // now using county
  const response = await fetch("/get_county_data", {           // updated endpoint
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ county })
  });

  const data = await response.json();

  // Handle "not found"
  if (data.error) {
    document.getElementById("result").innerHTML = `<p>${data.error}</p>`;
    return;
  }

  document.getElementById("result").innerHTML = `
    <h2>${data.name}</h2>
    <p><strong>Average Weather:</strong> ${data.averageWeather}</p>
    <p><strong>Average Cost of Living:</strong> ${data.averageCostOfLiving}</p>
    <p><strong>Crime & Safety:</strong> ${data.crimeSafety}</p>
    <p><strong>School Quality:</strong> ${data.schoolQuality}</p>
    <p><strong>Diversity:</strong> ${data.diversityPercent}%</p>
  `;
});
