const images = [
  "static/images/pexels-changerstudio-140831.jpg",
  "static/images/pexels-cottonbro-3825294.jpg",
  "static/images/pexels-cottonbro-4684185.jpg",
  "static/images/pexels-dan-prado-141463-428124.jpg",
  "static/images/pexels-designecologist-905938.jpg",
  "static/images/pexels-f4photography-1317365.jpg",
  "static/images/pexels-george-dolgikh-551816-2072149.jpg",
  "static/images/pexels-jessbaileydesign-913136 (1).jpg",
  "static/images/pexels-jessbaileydesign-913136.jpg",
  "static/images/pexels-lilartsy-1793037.jpg",
  "static/images/pexels-marinautrabo-1729797.jpg",
  "static/images/pexels-marinautrabo-1729808.jpg",
  "static/images/pexels-nietjuh-3123915.jpg",
  "static/images/pexels-pixabay-45238.jpg",
  "static/images/pexels-pixabay-264787.jpg",
  "static/images/pexels-psco-1071878.jpg",
  "static/images/pexels-rodrigo-souza-1275988-2531546.jpg",
  "static/images/pexels-thatguycraig000-1543762.jpg",
  "static/images/pexels-wdnet-172500.jpg",
  "static/images/pexels-wdnet-226737.jpg",
];

// Function to change background image
function changeBackground() {
  const img = document.querySelector(".img");
  const randomIndex = Math.floor(Math.random() * images.length);
  img.style.backgroundImage = `url(${images[randomIndex]})`;
  img.style.backgroundSize = "cover"; // Ensure the image covers the body
  img.style.backgroundPosition = "center"; // Center the image
  img.style.backgroundRepeat = "no-repeat"; // Prevent image repeat
}

// Change background on page load
window.onload = changeBackground;
