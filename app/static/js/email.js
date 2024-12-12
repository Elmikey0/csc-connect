document.getElementById("delete-btn")?.addEventListener("click", (e) => {
  e.preventDefault(); // Prevent the default form submission
  if (confirm("Do you really want to delete this record?")) {
    // If the user confirms, submit the form
    e.target.closest("form").submit(); // Submit the form that contains the button
  }
});

document.getElementById("admin-email")?.addEventListener("click", (e) => {
  e.preventDefault();
  if (confirm("Do you really want to leave this page?")) {
    window.location.href = e.target.getAttribute("href");
  }
});
