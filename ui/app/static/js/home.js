// 1) Add shadow when scrolled
// 2) Make header “glassy” while any dropdown is hovered
const header = document.getElementById("siteHeader");
const navGroup = document.getElementById("navGroup");

function onScroll(){
  // Toggles the class 'scrolled' if vertical scroll is > 6px
  header.classList.toggle("scrolled", window.scrollY > 6);
}

// Passive listener is better for performance
window.addEventListener("scroll", onScroll, { passive: true });
onScroll();

// Glass effect toggle on hover
navGroup.addEventListener("mouseenter", () => header.classList.add("menu-open"));
navGroup.addEventListener("mouseleave", () => header.classList.remove("menu-open"));