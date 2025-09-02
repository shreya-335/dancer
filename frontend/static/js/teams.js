async function submitTeam(e){
  e.preventDefault();
  const teamName = document.getElementById("teamName").value;
  const leaderName = document.getElementById("leaderName").value;
  const leaderEmail = document.getElementById("leaderEmail").value;
  const members = document.getElementById("members").value.split(",").map(s=>s.trim());
  const category = document.getElementById("category").value;
  const res = await fetch("/api/register-team", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({team_name:teamName, leader_name:leaderName, leader_email:leaderEmail, members, category})
  });
  const j = await res.json();
  alert(j.message || j.status);
  if(j.status === "success") document.getElementById("teamForm").reset();
}
