// Load the LIFF SDK
liff.init({
    liffId: '1657441828-D9LqXa0V'
}).then(() => {
    // Get the user ID from the access token
    const accessToken = liff.getAccessToken();
    liff.getProfile().then(profile => {
        const userId = profile.userId;

        // Bind the user ID to the user account in Django
        const url = '/bind_user_account/';
        const data = { user_id: userId, access_token: accessToken };
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).then(response => {
            console.log(response);
        }).catch(error => {
            console.error(error);
        });

        // Display the user ID in the HTML page
        document.getElementById('userId').textContent = userId;
    }).catch(error => {
        console.error(error);
    });
}).catch(error => {
    console.error(error);
});
