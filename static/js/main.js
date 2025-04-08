// Function to fetch and display employees on the home page.
async function loadEmployees() {
  try {
    const response = await fetch("/employees/get_employees");
    const html = await response.text();
    // Render the returned HTML into the employee-list div
    document.getElementById("employee-list").innerHTML = html;
  } catch (error) {
    console.error("Error loading employees:", error);
  }
}

// Call loadEmployees when the page loads (if on the home page)
if (document.getElementById("employee-list")) {
  loadEmployees();
}

// Function to create a new employee via the API.
async function createEmployee() {
  const form = document.getElementById("add-employee-form");
  const formData = new FormData(form);
  const data = Object.fromEntries(formData.entries());

  try {
    const response = await fetch("/employees/create-employees/", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data)
    });
    const result = await response.json();
    document.getElementById("employee-msg").innerText = "Employee created successfully!";
    // Optionally, refresh the employee list
    loadEmployees();
  } catch (error) {
    console.error("Error creating employee:", error);
    document.getElementById("employee-msg").innerText = "Error creating employee.";
  }
}
