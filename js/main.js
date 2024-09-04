// function to go to sign up & sign in from login page with sound
function loadPage(nextPageId) {
    const currentPage = document.querySelector('.active');
    const nextPage = document.getElementById(nextPageId);
    const transitionSound = document.getElementById('transition-sound');

    // Play the sound
    transitionSound.play();

    // Add class to slide the current page out
    currentPage.classList.add('slide-out');
    
    // After the slide-out animation, switch pages
    setTimeout(function() {
        // Remove the active class and transition classes from the current page
        currentPage.classList.remove('active');
        currentPage.classList.remove('slide-out');

        // Add classes to make the new page slide in
        nextPage.classList.add('active');
        nextPage.classList.add('slide-in');

        // Clean up after the animation
        setTimeout(function() {
            nextPage.classList.remove('slide-in');
        }, 500); // Match this duration with your CSS transition time
    }, 500); // Match this duration with your CSS transition time
}
