const cards = document.querySelectorAll(".linkcard:not(.disabled)");
for (const c of cards) {
  c.addEventListener("mousedown", () => c.classList.add("pressed"));
  c.addEventListener("mouseup", () => c.classList.remove("pressed"));
  c.addEventListener("mouseleave", () => c.classList.remove("pressed"));
}
