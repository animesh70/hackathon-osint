// Add marker to map based on post type
function addMarker(post) {
    const location = post.location;
    if (!location) return;
    
    let marker, circle;
    
    if (location.type === 'exact') {
        marker = createExactMarker(post);
    } else if (location.type === 'approx') {
        const result = createApproxMarker(post);
        marker = result.marker;
        circle = result.circle;
        if (circle) markers.push(circle);
    } else if (location.type === 'cluster') {
        marker = createClusterMarker(post);
    }
    
    if (marker) {
        markers.push(marker);
        
        // Add click event to focus on post in sidebar
        marker.on('click', function() {
            focusOnPost(post.id);
        });
    }
}

// Create exact location marker (red pin)
function createExactMarker(post) {
    const loc = post.location;
    const marker = L.marker([loc.lat, loc.lng], {
        icon: L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: #dc3545; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">📍</div>',
            iconSize: [30, 30]
        })
    }).addTo(map);
    
    marker.bindPopup(createPopupContent(post, '🔴 Exact Location'));
    return marker;
}

// Create approximate location marker (yellow circle)
function createApproxMarker(post) {
    const loc = post.location;
    const circle = L.circle([loc.lat, loc.lng], {
        color: '#ffc107',
        fillColor: '#ffc107',
        fillOpacity: 0.2,
        radius: loc.radius || 20000
    }).addTo(map);
    
    const marker = L.marker([loc.lat, loc.lng], {
        icon: L.divIcon({
            className: 'custom-marker',
            html: '<div style="background: #ffc107; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 18px; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">❓</div>',
            iconSize: [30, 30]
        })
    }).addTo(map);
    
    marker.bindPopup(createPopupContent(post, '🟡 Approximate Region'));
    
    return { marker, circle };
}

// Create cluster marker (green)
function createClusterMarker(post) {
    const loc = post.location;
    const marker = L.marker([loc.lat, loc.lng], {
        icon: L.divIcon({
            className: 'custom-marker',
            html: `<div style="background: #28a745; width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 16px; font-weight: bold; box-shadow: 0 2px 10px rgba(0,0,0,0.3);">${loc.count || 2}</div>`,
            iconSize: [40, 40]
        })
    }).addTo(map);
    
    marker.bindPopup(createPopupContent(post, '🟢 Activity Cluster'));
    return marker;
}

// Create popup content
function createPopupContent(post, title) {
    const loc = post.location;
    const color = getColorForType(loc.type);
    
    let content = `
        <div style="min-width: 200px;">
            <h4 style="color: ${color}; margin-bottom: 8px;">${title}</h4>
            <p><strong>Location:</strong> ${loc.location}</p>
            <p><strong>Date:</strong> ${formatDate(post.date)}</p>
            <p><strong>Source:</strong> ${loc.description}</p>
    `;
    
    if (loc.imageFeatures && loc.imageFeatures.length > 0) {
        content += `<p><strong>Features:</strong><br>${loc.imageFeatures.join(', ')}</p>`;
    }
    
    if (post.caption) {
        content += `<p><strong>Caption:</strong> ${post.caption}</p>`;
    }
    
    if (loc.count) {
        content += `<p><strong>Posts:</strong> ${loc.count} from this area</p>`;
    }
    
    content += `<p><strong>Confidence:</strong> <span style="color: ${getConfidenceColor(loc.confidence)};">${loc.confidence.toUpperCase()}</span></p>`;
    
    if (loc.radius) {
        content += `<p style="font-size: 0.85em; color: #666; margin-top: 8px;"><em>Radius: ~${(loc.radius/1000).toFixed(0)} km</em></p>`;
    }
    
    content += '</div>';
    return content;
}

// Add movement path between two posts
function addMovementPath(fromPost, toPost) {
    const fromLoc = fromPost.location;
    const toLoc = toPost.location;
    
    if (!fromLoc || !toLoc) return;
    
    const latlngs = [
        [fromLoc.lat, fromLoc.lng],
        [toLoc.lat, toLoc.lng]
    ];
    
    const path = L.polyline(latlngs, {
        color: '#6c757d',
        weight: 2,
        opacity: 0.6,
        dashArray: '10, 10'
    }).addTo(map);
    
    const from = new Date(fromPost.date);
    const to = new Date(toPost.date);
    const daysDiff = Math.round((to - from) / (1000 * 60 * 60 * 24));
    
    path.bindPopup(`
        <div style="min-width: 200px;">
            <h4 style="color: #6c757d; margin-bottom: 8px;">🧭 Inferred Movement</h4>
            <p><strong>From:</strong> ${fromLoc.location}</p>
            <p><strong>To:</strong> ${toLoc.location}</p>
            <p><strong>Time gap:</strong> ${daysDiff} days</p>
            <p style="font-size: 0.85em; color: #666; margin-top: 8px;"><em>Note: This shows inferred movement between posts, not actual travel route or method.</em></p>
        </div>
    `);
    
    paths.push(path);
}

// Helper functions
function getColorForType(type) {
    switch(type) {
        case 'exact': return '#dc3545';
        case 'approx': return '#ffc107';
        case 'cluster': return '#28a745';
        default: return '#6c757d';
    }
}

function getConfidenceColor(confidence) {
    switch(confidence.toLowerCase()) {
        case 'high': return '#28a745';
        case 'medium': return '#ffc107';
        case 'low': return '#dc3545';
        default: return '#6c757d';
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}