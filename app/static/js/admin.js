document.getElementById("edit-btn")?.addEventListener("click", (e) => {
  e.preventDefault();
  if (confirm("Do you want to leave this page?")) {
    window.location.href = e.target.href;
  }
});
document.getElementById("admin-email")?.addEventListener("click", (e) => {
  e.preventDefault();
  if (confirm("Do you want to leave this page?")) {
    window.location.href = e.target.href;
  }
});
