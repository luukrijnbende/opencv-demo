const DEFAULT_RESOLUTION = { width: 1280, height: 720 }

const loader = document.getElementById("loader");

async function loadOpenCV(threads = 1) {
  const openCV = await cv;
  // Set the number of threads OpenCV can use.
  // You can increase this to increase performance.
  // Setting this to anything higher than 1 will give a warning about blocking the main thread.
  // I haven't found out how fix this when building OpenCV.
  openCV.parallel_pthreads_set_threads_num(threads);
  console.log(`Loaded OpenCV version ${getOpenCVVersion(openCV)} with ${threads} thread(s).`);
  return openCV;
}

function getOpenCVVersion(openCV) {
  const buildString = openCV.getBuildInformation();
  return buildString.split("Version control:")[1].split("\n")[0].trim();
}

async function startCamera(resolution) {
  return navigator.mediaDevices.getUserMedia({
    video: {
      width: { exact: resolution.width },
      height: { exact: resolution.height },
    },
    audio: false,
  });
}

async function playStream(videoElement, stream) {
  videoElement.srcObject = stream;
  videoElement.play();

  // Wait for the video to start playing.
  return new Promise((resolve) => {
    videoElement.addEventListener("canplay", () => {
      resolve();
    });
  });
}

function prepareOutput(output, resolution) {
  output.width = resolution.width;
  output.height = resolution.height;

  const outputContext = output.getContext("2d");
  outputContext.lineWidth = 3;
  outputContext.strokeStyle = "#b80f0a";
  outputContext.font = "32px Arial";
  outputContext.fillStyle = "#b80f0a";
}

function setLoading(loading) {
  if (!loader) return;

  if (loading) loader.classList.remove("hidden");
  else loader.classList.add("hidden");
}

function createProcessingCanvas(resolution) {
  const processingCanvas = document.createElement("canvas");
  processingCanvas.width = resolution.width;
  processingCanvas.height = resolution.height;

  return processingCanvas;
}

function drawFPS(output, duration) {
  output.getContext("2d").fillText(Math.round(1000 / duration), output.width - 50, 40);
}