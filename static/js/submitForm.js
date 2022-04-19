const dropArea = document.querySelector(".drag-area"),
button = dropArea.querySelector("button"),
dragText = dropArea.querySelector("header");
const input = document.querySelector(".drag-input-file");
let file;

button.onclick = () => {
  input.click();
};

input.addEventListener("change", function () {
file = this.files[0];
dropArea.classList.add("active");
showFile();
});

// dropArea.addEventListener("dragover", (event) => {
// event.preventDefault();
// console.log("in drop area");
// dropArea.classList.add("active");
// dragText.textContent = "Release to Upload File";
// });

// dropArea.addEventListener("dragleave", () => {
// console.log("outside");
// dropArea.classList.remove("active");
// dragText.textContent = "Drag & Drop to Upload File";
// });

// dropArea.addEventListener("drop", (event) => {
// event.preventDefault();
// file = event.dataTransfer.files[0];
// console.log(file);
// showFile();
// });

function showFile() {
let fileType = file.type;
let validImageExtensions = ["image/jpeg", "image/jpg", "image/png"];
let validVideoExtensions = ["video/webm", "video/mp4"];
if (validImageExtensions.includes(fileType)) {
  let fileReader = new FileReader();
  fileReader.onload = () => {
    let fileURL = fileReader.result;
    let imgTag = `<img src="${fileURL}" alt="">`;
    dropArea.innerHTML = imgTag;
  };
  fileReader.readAsDataURL(file);
} else if (validVideoExtensions.includes(fileType)) {
  let fileReader = new FileReader();
  fileReader.onload = () => {
    let fileURL = fileReader.result;
    let videoTag = `<video>
                    <source src="${fileURL}" type="">
                    </video>`;
    dropArea.innerHTML = videoTag;
  };
  fileReader.readAsDataURL(file);
} else {
  alert("This is not an Image File!");
  dropArea.classList.remove("active");
  dragText.textContent = "Drag & Drop to Upload File";
}
}
