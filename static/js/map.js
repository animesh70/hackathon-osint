let map;
let markers = [];
let paths = [];
let currentData = [];

// Initialize map
function initMap() {
    map = L.map('map').setView([20.5937, 78.9629], 5);
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18
    }).addTo(map);
}

// Clear all markers and paths from map
function clearMap() {
    markers.forEach(marker => {
        if (map.hasLayer(marker)) {
            map.removeLayer(marker);
        }
    });
    paths.forEach(path => {
        if (map.hasLayer(path)) {
            map.removeLayer(path);
        }
    });
    markers = [];
    paths = [];
}

// Fit map to show all markers
function fitMapToMarkers() {
    if (markers.length > 0) {
        const group = L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Initialize map on load
window.addEventListener('DOMContentLoaded', function() {
    initMap();
});