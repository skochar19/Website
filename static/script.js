document.getElementById("submitBtn").addEventListener("click", async () => {
    const city = document.getElementById("cityInput").value;
    const response = await fetch("/get_city_data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city })
    });
  
    const data = await response.json();
    document.getElementById("result").innerHTML = `
      <h2>${data.city}</h2>
      <p>Cost of Living: ${data.cost_of_living}</p>
      <p>Weather: ${data.weather}</p>
      <p>Walkability: ${data.walkability}</p>
      <p>School Quality: ${data.school_quality}</p>
      <p>Crime Rate: ${data.crime_rate}</p>
    `;
  });
  