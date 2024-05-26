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
    const response = await fetch("/?format=json");
    const items = await response.json();
    updateMap(items);
}

function addPropertiesToMap(items) {
    items = JSON.parse(items);
    updateMap(items);
}

showPropertiesOnMap();