// Function to get the value of a URL query parameter
function getQueryParam(name) {
  const queryString = window.location.search;
  const urlParams = new URLSearchParams(queryString);
  return urlParams.get(name);
}

document.addEventListener("DOMContentLoaded", function () {
  const code = document.querySelector("code");
  const email = getQueryParam("email");
  const data = {
    email: email,
    username: email,
  };
  let xhttp = new XMLHttpRequest();
  xhttp.open("Post", "http://127.0.0.1:8080/tfa", true);
  xhttp.setRequestHeader("Content-Type", "application/json");
  xhttp.onreadystatechange = function () {
    if (xhttp.readyState === XMLHttpRequest.DONE) {
      if (xhttp.status === 200) {
        // Successful login
        console.log("TFA successful!");
        console.log(xhttp.responseText);
        code.innerHTML += JSON.parse(xhttp.responseText)["tfa_code"];
      } else {
        // Failed login
        console.log("TFA failed!");
        console.log(xhttp.responseText);
      }
    }
  };
  xhttp.send(JSON.stringify(data));
});
