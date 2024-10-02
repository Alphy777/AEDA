// Handle panel for sign-in and sign-up
const signInButton = document.getElementById('signIn');
const signUpButton = document.getElementById('signUp');
const container = document.getElementById('container');

signUpButton.addEventListener('click', () => {
  container.classList.add('right-panel-active');
});

signInButton.addEventListener('click', () => {
  container.classList.remove('right-panel-active');
});

document.addEventListener('DOMContentLoaded', function() {
  const inboxTab = document.getElementById('inboxTab');
  const sendTab = document.getElementById('sendTab');
  const inboxSection = document.querySelector('.inbox-section');
  const sendSection = document.querySelector('.send-section');
  
  // Show Inbox by default
  inboxSection.classList.add('active');
  
  // Inbox button click
  inboxTab.addEventListener('click', function(event) {
      event.preventDefault();
      inboxSection.classList.add('active');
      sendSection.classList.remove('active');
  });
  
  // Send button click
  sendTab.addEventListener('click', function(event) {
      event.preventDefault();
      sendSection.classList.add('active');
      inboxSection.classList.remove('active');
  });
});

