// Global state
let currentData = [];
let markers = [];

// ---------- MAIN ANALYSIS ----------

async function analyzeData() {
    const username = document.getElementById('username').value.trim();
    const platform = document.getElementById('platform').value;
    const postsList = document.getElementById('postsList');

    if (!username) {
        alert("Please enter a username");
        return;
    }

    postsList.innerHTML = '<div class="loading">🔄 Analyzing posts...</div>';

    try {
        const result = await ApiClient.analyzeUser(username, platform);

        if (!result.success) {
            postsList.innerHTML =
                `<div style="color:#dc3545; padding:20px;">
                    Error: ${result.error || "Analysis failed"}
                </div>`;
            return;
        }

        currentData = result.posts || [];

        clearMap();
        postsList.innerHTML =
            '<h3 style="margin-bottom: 15px; color:#333;">📍 Found Posts</h3>';

        currentData.forEach((post, index) => {
            addMarker(post);
            addPostToList(post, postsList);

            if (index > 0) {
                addMovementPath(currentData[index - 1], post);
            }
        });

        fitMapToMarkers();
        updateStatistics(result.statistics);

    } catch (error) {
        console.error("Analyze Error:", error);
        postsList.innerHTML =
            '<div style="color:#dc3545; padding:20px;">Error loading data. Please try again.</div>';
    }
}

// ---------- CLEAR ANALYSIS ----------

function clearAnalysis() {
    clearMap();
    currentData = [];
    document.getElementById('postsList').innerHTML = '';
    document.getElementById('stats').style.display = 'none';
    map.setView([20.5937, 78.9629], 5);
}

// ---------- ADD POST ITEM TO LIST ----------

function addPostToList(post, container) {
    const loc = post.location;
    if (!loc) return;

    const postDiv = document.createElement('div');
    postDiv.className = 'post-item';
    postDiv.setAttribute('data-post-id', post.id || '');

    let icon = '🟡';
    if (loc.type === 'exact') icon = '🔴';
    else if (loc.type === 'cluster') icon = '🟢';

    postDiv.innerHTML = `
        <h4>${icon} ${loc.location || "Unknown Location"}</h4>
        <p><strong>Date:</strong> ${formatDate(post.date)}</p>
        <p><strong>Type:</strong> ${loc.description || loc.type}</p>

        ${loc.imageFeatures?.length
            ? `<p><strong>Identified:</strong> ${loc.imageFeatures.join(', ')}</p>`
            : ''}

        ${loc.count
            ? `<p><strong>Posts:</strong> ${loc.count} from this area</p>`
            : ''}

        <span class="confidence ${loc.confidence || ''}">
            Confidence: ${(loc.confidence || '').toUpperCase()}
        </span>
    `;

    // Zoom to marker on click
    postDiv.addEventListener('click', () => {
        const marker = markers.find(m =>
            m.getLatLng &&
            Math.abs(m.getLatLng().lat - loc.lat) < 0.0001 &&
            Math.abs(m.getLatLng().lng - loc.lng) < 0.0001
        );

        if (marker) {
            map.setView([loc.lat, loc.lng], 12);
            marker.openPopup();
        }

        focusOnPost(post.id);
    });

    container.appendChild(postDiv);
}

// ---------- FOCUS ON POST IN LIST ----------

function focusOnPost(postId) {
    if (!postId) return;

    const postElement = document.querySelector(`[data-post-id="${postId}"]`);

    if (!postElement) return;

    postElement.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    postElement.style.backgroundColor = '#e7f3ff';

    setTimeout(() => {
        postElement.style.backgroundColor = 'white';
    }, 1000);
}

// ---------- UPDATE STATISTICS ----------

function updateStatistics(stats = {}) {
    document.getElementById('stats').style.display = 'block';
    document.getElementById('totalPosts').textContent = stats.total || 0;
    document.getElementById('exactCount').textContent = stats.exact || 0;
    document.getElementById('approxCount').textContent = stats.approx || 0;
    document.getElementById('timeSpan').textContent = stats.time_span || "—";
}

// ---------- EXPORT DATA ----------

async function exportData() {
    const username = document.getElementById('username').value.trim();

    if (!username) {
        alert("Enter username before exporting");
        return;
    }

    try {
        const result = await ApiClient.exportAnalysis(username);

        if (!result.success) {
            alert("❌ Export failed");
            return;
        }

        const dataStr = JSON.stringify(result.data, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);

        const link = document.createElement("a");
        link.href = url;
        link.download = result.filename || "analysis.json";
        link.click();

        alert('✅ Data exported successfully!');
    } catch (err) {
        console.error("Export error:", err);
        alert("❌ Error exporting data");
    }
}

// ---------- TIMELINE MODAL ----------

function toggleTimeline() {
    const modal = document.getElementById('timelineModal');

    if (modal.style.display === "flex") {
        modal.style.display = "none";
        return;
    }

    if (!currentData.length) {
            alert('No data to display. Please analyze a user first.');
            return;
    }

    populateTimeline();
    modal.style.display = "flex";
}

// ---------- POPULATE TIMELINE ----------

function populateTimeline() {
    const timelineBody = document.getElementById('timelineBody');
    timelineBody.innerHTML = '';

    const sorted = [...currentData].sort(
        (a, b) => new Date(a.date) - new Date(b.date)
    );

    sorted.forEach(post => {
        const loc = post.location;
        if (!loc) return;

        const timelineItem = document.createElement('div');
        timelineItem.className = 'timeline-item';

        const icon =
            loc.type === 'exact' ? '📍' :
            loc.type === 'cluster' ? '🟢' :
            '❓';

        timelineItem.innerHTML = `
            <div class="timeline-dot">${icon}</div>
            <div class="timeline-item-content">
                <h4>${loc.location || "Unknown Location"}</h4>

                <p><strong>Date:</strong> ${formatDate(post.date)}</p>

                <p><strong>Type:</strong>
                    ${loc.type?.toUpperCase()} (${loc.confidence || "n/a"} confidence)
                </p>

                ${post.caption
                    ? `<p><strong>Caption:</strong> ${post.caption}</p>`
                    : ''}

                ${loc.imageFeatures?.length
                    ? `<p><strong>Features:</strong> ${loc.imageFeatures.join(', ')}</p>`
                    : ''}
            </div>
        `;

        timelineBody.appendChild(timelineItem);
    });
}

// ---------- HELPERS ----------

function formatDate(dateStr) {
    if (!dateStr) return "Unknown";
    return new Date(dateStr).toLocaleDateString();
}