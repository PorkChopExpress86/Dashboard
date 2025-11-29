// Main client-side JS
document.addEventListener('DOMContentLoaded', () => {
  initRadarMap();
  initGeolocation();
});

// Initialize the weather radar map using Leaflet and RainViewer
function initRadarMap() {
  const radarEl = document.getElementById('radar-map');
  if (!radarEl) return;

  const lat = parseFloat(radarEl.dataset.lat) || 41.8781;
  const lon = parseFloat(radarEl.dataset.lon) || -87.6298;

  const map = L.map('radar-map').setView([lat, lon], 7);

  // Base tile layer (OpenStreetMap)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; OpenStreetMap contributors'
  }).addTo(map);

  // Add marker for current location
  L.marker([lat, lon]).addTo(map)
    .bindPopup('Your Location')
    .openPopup();

  // Fetch RainViewer radar frames and add the latest
  fetchRadarLayer(map);
}

// Fetch radar data from RainViewer API
async function fetchRadarLayer(map) {
  try {
    const response = await fetch('https://api.rainviewer.com/public/weather-maps.json');
    const data = await response.json();
    
    if (data.radar && data.radar.past && data.radar.past.length > 0) {
      // Get the most recent radar frame
      const latestFrame = data.radar.past[data.radar.past.length - 1];
      const radarPath = latestFrame.path;
      
      // Add radar tile layer
      const radarLayer = L.tileLayer(`https://tilecache.rainviewer.com${radarPath}/256/{z}/{x}/{y}/2/1_1.png`, {
        opacity: 0.6,
        attribution: '&copy; RainViewer'
      });
      radarLayer.addTo(map);

      // Update radar layer every 5 minutes
      setInterval(async () => {
        try {
          const newResponse = await fetch('https://api.rainviewer.com/public/weather-maps.json');
          const newData = await newResponse.json();
          if (newData.radar && newData.radar.past && newData.radar.past.length > 0) {
            const newLatestFrame = newData.radar.past[newData.radar.past.length - 1];
            radarLayer.setUrl(`https://tilecache.rainviewer.com${newLatestFrame.path}/256/{z}/{x}/{y}/2/1_1.png`);
          }
        } catch (e) {
          console.error('Error updating radar:', e);
        }
      }, 300000); // 5 minutes
    }
  } catch (error) {
    console.error('Error fetching radar data:', error);
  }
}

// Initialize browser geolocation
function initGeolocation() {
  if (!navigator.geolocation) {
    console.log('Geolocation not supported');
    return;
  }

  // Request location on page load
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;
      console.log(`Location detected: ${lat}, ${lon}`);
      
      // Store in sessionStorage for future use
      sessionStorage.setItem('userLat', lat.toString());
      sessionStorage.setItem('userLon', lon.toString());
      
      // Update the radar map if it exists
      updateRadarMapLocation(lat, lon);
    },
    (error) => {
      console.log('Geolocation error:', error.message);
      // Fall back to configured location (already displayed)
    },
    {
      enableHighAccuracy: false,
      timeout: 10000,
      maximumAge: 300000 // Cache for 5 minutes
    }
  );
}

// Update radar map center and marker when geolocation succeeds
function updateRadarMapLocation(lat, lon) {
  const radarEl = document.getElementById('radar-map');
  if (!radarEl || !radarEl._leaflet_map) {
    // Map not initialized yet via Leaflet internal reference
    // Try to find map through L.map instances
    return;
  }
  
  // If we have access to the map instance, update it
  // This is a simple approach - in production you'd store the map reference
}
