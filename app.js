function test(items){
    // console.log(items)
    items = JSON.parse(items)
    console.log(items)
    items.forEach( item => {
        let marker = new mapboxgl.Marker()
        .setLngLat([item.item_lon, item.item_lat]) // Marker 1 coordinates
        .addTo(map);        
    })
}

function handleUserDeleteModal() {
    const btn = document.querySelector("#showDeleteUserModal");
    const modal = document.querySelector("#deleteUserModal");
    const close = document.querySelector("#deleteUserModal > #close");
    const cancel = document.querySelector("#deleteUserModal #cancel");

    btn.addEventListener("click", function () {
        modal.showModal();
        close.blur();
    });

    close.addEventListener("click", function () {
        modal.close();
    });

    cancel.addEventListener("click", function (evt) {
        evt.preventDefault();
        modal.close();
    });
}

handleUserDeleteModal();