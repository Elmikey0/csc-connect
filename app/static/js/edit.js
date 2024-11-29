document.addEventListener("DOMContentLoaded", function () {
  const detailsForm = document.getElementById("details");
  const editForm = document.getElementById("edit-form");

  function setInitialVisibility() {
    if (detailsForm && editForm) {
      detailsForm.classList.remove("hidden");
      editForm.classList.add("hidden");
    }
  }

  // Show edit form and hide the registration form
  function showEditForm() {
    if (detailsForm && editForm) {
      detailsForm.classList.add("hidden");
      editForm.classList.remove("hidden");
      console.log("Showing edit form");
    }
  }

  // Show registration form and hide edit form
  function showRegistrationForm() {
    if (detailsForm && editForm) {
      detailsForm.classList.remove("hidden");
      editForm.classList.add("hidden");
      console.log("Showing registration form");
    }
  }

  // Call function
  setInitialVisibility();
});

document.getElementById("delete-btn")?.addEventListener("click", (e) => {
  e.preventDefault();
  if (confirm("Do you really want to delete this record?")) {
    window.location.href = e.target.href;
  }
});
