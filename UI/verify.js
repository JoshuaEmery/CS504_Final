// Function to get the value of a URL query parameter
function getQueryParam(name) {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  return urlParams.get(name);
}

// Get the username from the URL query parameter
const username = getQueryParam("email");
if (!username) {
  document.body.innerHTML = "No email provided!";
} else {
  // Display the username on the page
  const form = document.getElementById("tfa-form");
  const usernameElement = document.createElement("input");
  usernameElement.setAttribute("type", "hidden");
  usernameElement.setAttribute("name", "username");
  usernameElement.setAttribute("value", username);
  form.appendChild(usernameElement);
  document.querySelector("h1").innerHTML += " - " + username;

  // send an ajax request to get the expiration time
  getExpirationTime();

  //set the link to view tfa code
  const tfaLink = document.getElementById("tfa-link");
  tfaLink.addEventListener("click", function () {
    const redirectUrl = "tfa.html?email=" + encodeURIComponent(username);
    window.open(redirectUrl, "_blank");
  });

  form.addEventListener("submit", sumbitForm);

  function sumbitForm(event) {
    event.preventDefault(); // Prevent the form from submitting normally

    // Get the form values
    const tfa_code = document.getElementById("tfa_code").value;

    // Create an object with the form data
    var formData = {
      username: username,
      tfa_code: tfa_code,
    };

    // Send the form data using AJAX
    let xhttp = new XMLHttpRequest();
    xhttp.open("POST", "http://127.0.0.1:8080/tfa/validate", true);
    xhttp.setRequestHeader("Content-Type", "application/json");
    xhttp.onreadystatechange = function () {
      if (xhttp.readyState === XMLHttpRequest.DONE) {
        if (xhttp.status === 200) {
          // Successful login
          console.log("TFA successful!");
          console.log(xhttp.responseText);
          document.body.innerHTML = xhttp.responseText;
        } else {
          // Failed login
          console.log("TFA failed!");
          console.log(xhttp.responseText);
          document.body.innerHTML = xhttp.responseText;
        }
      }
    };
    xhttp.send(JSON.stringify(formData));
  }

  function getExpirationTime() {
    let xhttp = new XMLHttpRequest();
    xhttp.open("GET", "http://127.0.0.1:8080/expiration", true);
    xhttp.onreadystatechange = function () {
      if (xhttp.readyState === XMLHttpRequest.DONE) {
        if (xhttp.status === 200) {
          // Successful login
          console.log(xhttp.responseText);
          const dateString = JSON.parse(xhttp.responseText)["expiration"];
          const expirationTime = new Date(dateString);
          startCountdown(expirationTime);
        } else {
          // Failed login
          console.log(xhttp.responseText);
        }
      }
    };
    xhttp.send();
  }

  function startCountdown(expirationTime) {
    let timer = setInterval(() => {
      const distance = expirationTime - new Date();
      // Calculate the time remaining
      // distance is in miliseconds
      // convert to minutes and take the floor
      const minutes = Math.floor((distance / 1000 / 60) % 60);
      const seconds = Math.floor((distance / 1000) % 60);
      //const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      //var seconds = Math.floor((distance % (1000 * 60)) / 1000);

      // Display the countdown timer on the page
      const countdownElement = document.getElementById("countdown-timer");
      countdownElement.innerHTML = `TFA Code expires in:${minutes}m ${seconds}s`;

      // When the countdown is finished, display a message
      if (distance < 0) {
        clearInterval(countdownTimer);
        countdownElement.innerHTML = "Expired";
      }
    }, 1000); // 1000 milliseconds = 1 second
  }
}
