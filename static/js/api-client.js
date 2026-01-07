// API Client for communicating with Flask backend
const API_BASE_URL = window.location.origin + '/api';

const ApiClient = {
    // Analyze user posts
    async analyzeUser(username, platform = 'instagram') {
        try {
            const response = await fetch(`${API_BASE_URL}/analyze`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username, platform })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error analyzing user:', error);
            throw error;
        }
    },

    // Get demo data
    async getDemoData() {
        try {
            const response = await fetch(`${API_BASE_URL}/demo-data`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting demo data:', error);
            throw error;
        }
    },

    // Calculate distance between two points
    async calculateDistance(lat1, lng1, lat2, lng2) {
        try {
            const response = await fetch(`${API_BASE_URL}/calculate-distance`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ lat1, lng1, lat2, lng2 })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error calculating distance:', error);
            throw error;
        }
    },

    // Export analysis results
    async exportAnalysis(username) {
        try {
            const response = await fetch(`${API_BASE_URL}/export`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ username })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error exporting analysis:', error);
            throw error;
        }
    },

    // Health check
    async healthCheck() {
        try {
            const response = await fetch(`${API_BASE_URL}/health`);
            return await response.json();
        } catch (error) {
            console.error('Error checking health:', error);
            throw error;
        }
    }
};