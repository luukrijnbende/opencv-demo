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
let maskMat = null;

async function start() {
  openCV = await loadOpenCV();
  stream = await startCamera(resolution);
  await playStream(input, stream);
  startProcessing();

  setLoading(false);
}

//#region OpenCV

function startProcessing() {
  processingCanvas = createProcessingCanvas(resolution);
  processingCanvasContext = processingCanvas.getContext("2d");

  srcMat = new openCV.Mat(resolution.height, resolution.width, openCV.CV_8UC4);
  grayMat = new openCV.Mat(resolution.height, resolution.width, openCV.CV_8UC1);

  requestAnimationFrame(processVideo);
}

function processVideo() {
  const begin = Date.now();
  const circleMat = new openCV.Mat();

  // Prepare the frame.
  processingCanvasContext.drawImage(input, 0, 0, resolution.width, resolution.height);
  const imageData = processingCanvasContext.getImageData(0, 0, resolution.width, resolution.height);
  srcMat.data.set(imageData.data);

  // Convert to grayscale.
  openCV.cvtColor(srcMat, grayMat, openCV.COLOR_RGBA2GRAY);
  // Downsample because we have big image.
  openCV.pyrDown(grayMat, grayMat);
  // Blur the image to reduce noise.
  openCV.medianBlur(grayMat, grayMat, 5);

  // Detect circles.
  // Params:
  // 4: dp - Inverse ratio of the accumulator resolution to the image resolution, 1 = same as input, 2 = half the input.
  // 5: minDist - Minimum distance between the centers of the circles.
  // 6: highThreshold - High threshold for the Canny edge detector (low is half).
  // 7: accumulatorThreshold - Accumulator threshold for the circle centers, smaller means more false circle may be detected.
  //    Circles with the largest accumulator will be returned first.
  // 8: Minimum circle radius.
  // 9: Maximum cirlce radius.
  openCV.HoughCircles(grayMat, circleMat, openCV.HOUGH_GRADIENT, 1, 35, 150, 25, 5, 40);
  
  // Form a 2 color mask.
  maskMat = new openCV.Mat.zeros(resolution.height, resolution.width, openCV.CV_8UC4);
  openCV.threshold(srcMat, maskMat, 120, 255, openCV.THRESH_BINARY);
  openCV.cvtColor(maskMat, maskMat, openCV.COLOR_RGB2GRAY);
  openCV.threshold(maskMat, maskMat, 230, 255, openCV.THRESH_BINARY);

  // Get the circles.
  const circles = getCircles(circleMat, grayMat.size());
  // Get the first color.
  for (const circle of circles) {
    circle.colors.push(getCircleColor(circle));
  }
  // Invert the mask.
  openCV.bitwise_not(maskMat, maskMat);
  // Get the second color.
  for (const circle of circles) {
    circle.colors.push(getCircleColor(circle));
  }


  // Draw.
  outputContext.drawImage(processingCanvas, 0, 0, resolution.width, resolution.height);
  drawCircles(circles);
  drawFPS(output, Date.now() - begin);

  // Cleanup.
  circleMat.delete();
  maskMat.delete();
  // Schedule a new render.
  requestAnimationFrame(processVideo);
}

function getCircles(circleMat, detectionSize) {
  const circles = [];
  const xRatio = resolution.width / detectionSize.width;
  const yRatio = resolution.height / detectionSize.height;

  for (let i = 0; i < circleMat.cols; ++i) {
    const index = i * 3;
    const x = circleMat.data32F[index] * xRatio;
    const y = circleMat.data32F[index + 1] * yRatio;
    const radius = circleMat.data32F[index + 2] * ((xRatio + yRatio) / 2);

    circles.push({ x, y, radius, colors: [] });
  }

  return circles;
}

function getCircleColor(circle) {
  // Create a mask the same size as our input and fill it with zeroes (black).
  const mask = new openCV.Mat.zeros(resolution.height, resolution.width, openCV.CV_8UC1);
  // Draw a white circle on the mask.
  openCV.circle(mask, new openCV.Point(circle.x, circle.y), circle.radius, [255, 255, 255, 255], -1);
  // Merge the masks.
  openCV.bitwise_and(maskMat, mask, mask);
  // Get the mean color of the masked circle in our input.
  const mean = openCV.mean(srcMat, mask);
  // Cleanup the mask.
  mask.delete();
  
  // Return the RGB values as integer.
  return [Math.round(mean[0]), Math.round(mean[1]), Math.round(mean[2])];
}

//#endregion

//#region Canvas 

function drawCircles(circles) {
  for (const circle of circles) {
    outputContext.beginPath();
    outputContext.strokeStyle = `#${circle.colors[0].map(c => c.toString(16).padStart(2, "0")).join("")}`;
    outputContext.arc(circle.x, circle.y, circle.radius, Math.PI * 1.5, circle.colors.length > 1 ? Math.PI * 0.5 : Math.PI * 1.5);
    outputContext.stroke();

    if (circle.colors.length > 1) {
      outputContext.beginPath();
      outputContext.strokeStyle = `#${circle.colors[1].map(c => c.toString(16).padStart(2, "0")).join("")}`;
      outputContext.arc(circle.x, circle.y, circle.radius, Math.PI * 0.5, Math.PI * 1.5);
      outputContext.stroke();
    }
  }
}

//#endregion
