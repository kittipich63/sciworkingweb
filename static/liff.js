    // Initialize Line LIFF app
    liff.init({
      liffId: '1657441828-D9LqXa0V'
    }).then(() => {
      if (liff.isLoggedIn()) {
        const userId = liff.getContext().userId;
        document.getElementById('user-id').textContent = userId;
        window.location.href = `/bind-line-user/${userId}/`;
      } else {
        liff.login();
      }
    }).catch((err) => {
      console.error(err);
    });