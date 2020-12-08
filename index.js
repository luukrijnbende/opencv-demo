const loader = document.getElementById("loader");
const input = document.getElementById("input");
const output = document.getElementById("output");
const outputContext = output.getContext("2d");

const videoWidth = 1280;
const videoHeight = 720;

output.width = videoWidth;
output.height = videoHeight;
outputContext.lineWidth = 3;
outputContext.strokeStyle = "#b80f0a";
outputContext.font = "32px Arial";
outputContext.fillStyle = "#b80f0a";

let stream = null;
let processingCanvas = null;
let processingCanvasContext = null;
let srcMat = null;
let grayMat = null;
let faceClassifier = null;
let faces = null;

function setLoading(loading) {
  if (loading) loader.classList.remove("hidden");
  else loader.classList.add("hidden");
}

async function start() {
  await startCamera();
  startProcessing();

  setLoading(false);
}

//#region Camera

async function startCamera() {
  stream = await navigator.mediaDevices.getUserMedia({ video: { width: { exact: videoWidth }, height: { exact: videoHeight } }, audio: false });
  input.srcObject = stream;
  input.play();

  // Wait for the video to start playing.
  return new Promise((resolve) => {
    input.addEventListener("canplay", () => {
      resolve();
    });
  });
}

//#endregion

//#region OpenCV

function startProcessing() {
  processingCanvas = document.createElement("canvas");
  processingCanvas.width = videoWidth;
  processingCanvas.height = videoHeight;
  processingCanvasContext = processingCanvas.getContext("2d");

  srcMat = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC4);
  grayMat = new cv.Mat(videoHeight, videoWidth, cv.CV_8UC1);

  faceClassifier = new cv.CascadeClassifier();
  faceClassifier.load("haarcascade_frontalface_default.xml");

  faces = new cv.RectVector();

  requestAnimationFrame(processVideo);
}

function processVideo() {
  const begin = Date.now();

  // Prepare the frame.
  processingCanvasContext.drawImage(input, 0, 0, videoWidth, videoHeight);
  const imageData = processingCanvasContext.getImageData(0, 0, videoWidth, videoHeight);
  srcMat.data.set(imageData.data);

  // Convert to grayscale.
  cv.cvtColor(srcMat, grayMat, cv.COLOR_RGBA2GRAY);

  // Downsample because we have big image.
  cv.pyrDown(grayMat, grayMat);
  cv.pyrDown(grayMat, grayMat);

  // Detect faces.
  faceClassifier.detectMultiScale(grayMat, faces);
  
  // Draw.
  outputContext.drawImage(processingCanvas, 0, 0, videoWidth, videoHeight);
  drawFaces(grayMat.size());
  drawFPS(Date.now() - begin);

  requestAnimationFrame(processVideo);
}

//#endregion

//#region Canvas

function drawFaces(detectionSize) {
  for (let i = 0; i < faces.size(); i++) {
    const face = faces.get(i);
    const xRatio = videoWidth/detectionSize.width;
    const yRatio = videoHeight/detectionSize.height;

    outputContext.strokeRect(face.x * xRatio, face.y * yRatio, face.width * xRatio, face.height * yRatio);
  }
}

function drawFPS(duration) {
  outputContext.fillText(Math.round(1000 / duration), videoWidth - 50, 40);
}

//#endregion