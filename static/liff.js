// Initialize Line LIFF app
liff.init({
  liffId: '1657441828-D9LqXa0V'
}).then(() => {
  document.getElementById('connectLineButton').addEventListener('click', () => {
    // Check if user is logged in to Line
    if (!liff.isLoggedIn()) {
      liff.login();
    } else {
      // Get user ID from LIFF context
      const userId = liff.getContext().userId;
      // Redirect to Django view to bind Line user ID to User account
      window.location.href = `/bind-line-user/${userId}/`;
    }
  });
}).catch((err) => {
  console.error(err);
});