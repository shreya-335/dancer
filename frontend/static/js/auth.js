// Simple client-side auth for demo (store user in localStorage)
function saveUser(user){ localStorage.setItem("dc_user", JSON.stringify(user)); updateUserDisplay(); }
function getUser(){ return JSON.parse(localStorage.getItem("dc_user") || "null"); }
function updateUserDisplay(){
  const u = getUser();
  const el = document.getElementById("userDisplay");
  if(el) el.innerText = u ? `Logged in: ${u.name} (${u.user_id})` : "Not logged in";
}

// Register
async function register(){
  const name=document.getElementById("regName").value;
  const email=document.getElementById("regEmail").value;
  const phone=document.getElementById("regPhone").value;
  const password=document.getElementById("regPassword").value;
  const res = await fetch("/api/register", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({name, email, password, phone})});
  const j = await res.json();
  if(j.status==="success"){
    // Immediately log in after successful registration
    const lr = await fetch("/api/login", {method:"POST", headers:{"Content-Type":"application/json"},
      body: JSON.stringify({email, password})});
    const lj = await lr.json();
    if(lj.status==="success"){
      saveUser({user_id:lj.user_id, name:lj.name, is_admin:lj.is_admin});
      // Redirect to home
      window.location.href = "/";
    } else {
      alert("Registered but auto-login failed: " + (lj.message||""));
    }
  } else {
    alert(j.message || j.status);
  }
}

// Login
async function login(){
  const email=document.getElementById("loginEmail").value;
  const password=document.getElementById("loginPassword").value;
  const res = await fetch("/api/login", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({email, password})});
  const j = await res.json();
  if(j.status==="success"){
    saveUser({user_id:j.user_id, name:j.name, is_admin:j.is_admin});
    // Redirect to home after login
    window.location.href = "/";
  } else {
    alert(j.message || "Login failed");
  }
}
function logout(){ localStorage.removeItem("dc_user"); updateUserDisplay(); alert("Logged out"); }

document.addEventListener("DOMContentLoaded", updateUserDisplay);
