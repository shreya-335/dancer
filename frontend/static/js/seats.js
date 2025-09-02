let seats = [];
let selectedSeat = null;

async function loadSeats(){
  const res = await fetch("/api/seats");
  seats = await res.json();
  renderSeats();
}

function renderSeats(){
  const container = document.getElementById("seatMap");
  if(!container) return;
  container.innerHTML = "";
  seats.forEach(s => {
    const div = document.createElement("div");
    div.className = "seat " + (s.status === "available" ? "available" : "booked");
    div.innerText = s.seat_code;
    if(s.status === "available"){
      div.addEventListener("click", ()=> selectSeat(s.seat_code, div));
    }
    container.appendChild(div);
  });
}

function selectSeat(code, el){
  // deselect previous
  const prev = document.querySelector(".seat.selected");
  if(prev) prev.classList.remove("selected");
  el.classList.add("selected");
  selectedSeat = code;
}

async function bookSelected(){
  const user = JSON.parse(localStorage.getItem("dc_user") || "null");
  if(!user) return alert("Please login first");
  if(!selectedSeat) return alert("Select a seat first");
  const res = await fetch("/api/book", {method:"POST", headers:{"Content-Type":"application/json"},
    body: JSON.stringify({user_id: user.user_id, seat_code: selectedSeat})});
  const j = await res.json();
  alert(j.message || j.status);
  if(j.status === "success") loadSeats();
}

document.addEventListener("DOMContentLoaded", loadSeats);
