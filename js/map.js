const map = new mapboxgl.Map({
    container: 'map',
    style: 'mapbox://styles/mapbox/streets-v11',
    center: [12.5683, 55.6761],
    zoom: 12
});

function updateMap(items) {
    items.forEach( item => {
        // create the popup
        const popup = new mapboxgl.Popup({ offset: 25 }).setText(
            item.item_name,
        );

        new mapboxgl.Marker()
        .setLngLat([item.item_lon, item.item_lat])
        .setPopup(popup) // sets a popup on this marker
        .addTo(map);        
    });
}

async function showPropertiesOnMap() {
    try {
        const response = await fetch("/?format=json");
        const data = await response.json();
        
        if (data.status === "success" && data.items) {
            updateMap(data.items);
        } else {
            console.error("Error loading map data:", data);
        }
    } catch (error) {
        console.error("Error fetching map data:", error);
    }
}

function addPropertiesToMap(items) {
    try {
        const data = JSON.parse(items);
        updateMap(data);
    } catch (error) {
        console.error("Error parsing map data:", error);
    }
}

showPropertiesOnMap();