const subscribeButtons = document.querySelectorAll('.subscribe-watchlist-button');
const unsubscribeButtons = document.querySelectorAll('.unfollow-watchlist-button');
const subscribeAPIURL = document.querySelector('#subscribe-to-watchlist-url').value;

subscribeButtons.forEach(btn => {
    btn.addEventListener('click',  (e) => {
        handleSubscription(btn, e);
    })
})

unsubscribeButtons.forEach(btn => {
    btn.addEventListener('click', (e) => {
        handleSubscription(btn, e);
    })
})

async function handleSubscription(btn, event) {
    event.preventDefault();
    const formData = new FormData();
    formData.append('watchlist_id', btn.dataset.watchlistId);
    formData.append('operation', btn.dataset.operation);
    btn.innerHTML = '<span class="donutSpinner smallSpinner"></span>';
    const response = await fetch(subscribeAPIURL, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': csrftoken,
        }
    })
    if (response.ok) {
        if (btn.dataset.operation === 'subscribe') {
            btn.dataset.operation = 'unsubscribe';
            btn.innerHTML = '<span class="material-symbols-outlined">notifications_off</span>';
        }
        else {
            btn.dataset.operation = 'subscribe';
            btn.innerHTML = '<span class="material-symbols-outlined">add_alert</span>';
        }
    }
}