const input = document.getElementById("input");
const output = document.getElementById("output");
const outputContext = output.getContext("2d");

const resolution = DEFAULT_RESOLUTION;

prepareOutput(output, resolution);

let openCV = null;
let stream = null;
let processingCanvas = null;
let processingCanvasContext = null;
let srcMat = null;
let grayMat = null;
let faceClassifier = null;
let faces = null;

async function start() {
  openCV = await loadOpenCV();
  stream = await startCamera(resolution);
  await playStream(input, stream);
  startProcessing();

  setLoading(false);
}

//#region OpenCV

function startProcessing() {
  processingCanvas = document.createElement("canvas");
  processingCanvas.width = resolution.width;
  processingCanvas.height = resolution.height;
  processingCanvasContext = processingCanvas.getContext("2d");

  srcMat = new openCV.Mat(resolution.height, resolution.width, openCV.CV_8UC4);
  grayMat = new openCV.Mat(resolution.height, resolution.width, openCV.CV_8UC1);

  faceClassifier = new openCV.CascadeClassifier();
  faceClassifier.load("haarcascade_frontalface_default.xml");

  faces = new openCV.RectVector();

  requestAnimationFrame(processVideo);
}

function processVideo() {
  const begin = Date.now();

  // Prepare the frame.
  processingCanvasContext.drawImage(input, 0, 0, resolution.width, resolution.height);
  const imageData = processingCanvasContext.getImageData(0, 0, resolution.width, resolution.height);
  srcMat.data.set(imageData.data);

  // Convert to grayscale.
  openCV.cvtColor(srcMat, grayMat, openCV.COLOR_RGBA2GRAY);

  // Downsample because we have big image.
  openCV.pyrDown(grayMat, grayMat);
  openCV.pyrDown(grayMat, grayMat);

  // Detect faces.
  faceClassifier.detectMultiScale(grayMat, faces);
  
  // Draw.
  outputContext.drawImage(processingCanvas, 0, 0, resolution.width, resolution.height);
  drawFaces(grayMat.size());
  drawFPS(output, Date.now() - begin);

  requestAnimationFrame(processVideo);
}

//#endregion

//#region Canvas

function drawFaces(detectionSize) {
  const xRatio = resolution.width / detectionSize.width;
  const yRatio = resolution.height / detectionSize.height;
  
  for (let i = 0; i < faces.size(); i++) {
    const face = faces.get(i);

    outputContext.strokeRect(face.x * xRatio, face.y * yRatio, face.width * xRatio, face.height * yRatio);
  }
}

//#endregion