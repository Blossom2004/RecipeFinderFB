const file = document.getElementById("file");
const preview = document.getElementById("preview");

if (file && preview) {
  file.addEventListener("change", () => {
    const f = file.files?.[0];
    if (!f) return;
    const url = URL.createObjectURL(f);
    preview.src = url;
    preview.style.display = "block";
  });
}
