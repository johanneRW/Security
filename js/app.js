function handleDeleteModal(modalId, btnId) {
    const btn = document.querySelector(btnId);
    const modal = document.querySelector(modalId);
    const close = document.querySelector(modalId + " > #close");
    const cancel = document.querySelector(modalId + " #cancel");
    
    if (btn === null || modal === null) {
        return;
    }

    btn.addEventListener("click", function (evt) {
        evt.preventDefault();
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

function handleImageModal(modalId, btnId) {
    const btns = document.querySelectorAll(btnId);

    if (btns === null) {
        return;
    }

    for (const btn of btns) {
        btn.addEventListener("click", function (evt) {
            evt.preventDefault();
            
            const itemPk = btn.dataset.item;
            const dialogId = "#" + modalId + "_" + itemPk;
            const modal = document.querySelector(dialogId);
            const close = document.querySelector(dialogId + " > #close");
            const cancel = document.querySelector(dialogId + " #cancel");

            // Update only the oldname field, preserve csrf_token
            if (btn.id !== "new") {
                const oldnameInput = modal.querySelector('input[name="oldname"]');
                const filename = modal.querySelector('p.filename');
                if (oldnameInput) oldnameInput.value = btn.id;
                if (filename) filename.innerText = btn.id;
            }

            modal.showModal();
            close.blur();

            close.addEventListener("click", function () {
                modal.close();
            });
        
            cancel.addEventListener("click", function (evt) {
                evt.preventDefault();
                modal.close();
            });
        });
    }
}

function closeModal () {
    const openModals = document.querySelectorAll("dialog");

    for (const openModal of openModals) {
        openModal.close();
    }

    updateModalEvents();
}

function updateModalEvents () {
    handleImageModal("imageCreateModal", ".showCreateImageModal");
    handleImageModal("imageUpdateModal", ".showUpdateImageModal");    
}



function handlePromoteToPartnerModal(modalId, btnId) {
    const btn = document.querySelector(btnId);
    const modal = document.querySelector(modalId);

    if (btn === null || modal === null) {
        return;
    }

    const close = modal.querySelector("#closePromote");
    const cancel = modal.querySelector("#cancelPromote");

    if (close === null || cancel === null) {
        return;
    }

    // Åbn dialogen, når knappen klikkes
    btn.addEventListener("click", function (evt) {
        evt.preventDefault();
        modal.showModal();
        close.blur(); // Fjern fokus fra luk-knappen
    });

    // Luk dialogen, når "close" knappen klikkes
    close.addEventListener("click", function () {
        modal.close();
    });

    // Luk dialogen, når "cancel" knappen klikkes
    cancel.addEventListener("click", function (evt) {
        evt.preventDefault();
        modal.close();
    });
}


handlePromoteToPartnerModal("#promoteToPartnerModal", "#showPromoteToPartnerModal");
handleDeleteModal("#deleteUserModal", "#showDeleteUserModal");

handleImageModal("imageCreateModal", ".showCreateImageModal");
handleImageModal("imageUpdateModal", ".showUpdateImageModal");

