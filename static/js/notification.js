function showNotification(message) {

    const notification = document.getElementById("notification");

    notification.innerText = message;
    notification.classList.add("show");

    setTimeout(() => {
        notification.classList.remove("show");
    }, 3000);
}