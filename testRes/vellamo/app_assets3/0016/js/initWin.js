// JavaScript Document<script type="text/javascript">
var gl, canvas, docWidth, docHeight, deltaJellyfishCount, lastDeltaJellyfishCount, lastLastDeltaJellyfishCount, lastLastLastDeltaJellyfishCount, startedTime;
var resultsReported = 0;
var TARGET_FPS = 20;
var ESTIMATE_FRAMETIME = 40; //Conservative estimate

function reportResults() {
  var elem, report;
  if (!resultsReported) {
    resultsReported = 1;
    elem = document.getElementById('frameRate');
    report = {};
    if (gl) {
      report["fps"] = localParam.fpsAverage;
      report["count"] = Param.jActualRenderedCount;
    } else {
      report["fps"] = 0;
      report["count"] = 0;
      report["webgl_not_supported"] = 1;
      // note: don't consider the absence of WebGL as a failure, just a Zero score
      //VellamoBenchmark.endWithResultsAndMessage(report, "WebGL not supported");
      //return;
    }
    VellamoBenchmark.endWithResultsJSON(report);
  }
}

function updateCount() {
  var fpsDiff, newCount;
  // find out how many to create/remove
  lastLastLastDeltaJellyfishCount = lastLastDeltaJellyfishCount;
  lastLastDeltaJellyfishCount = lastDeltaJellyfishCount;
  lastDeltaJellyfishCount = deltaJellyfishCount;
  deltaJellyfishCount = 0;

  //Help with rapid convergence
  if (localParam.fpsAverage < 60 && localParam.fpsAverage > (TARGET_FPS + 5)) {
    var currentFrameTime = 1000/localParam.fpsAverage;
    newCount = Math.round(ESTIMATE_FRAMETIME * Param.jCount / currentFrameTime);
    deltaJellyfishCount = newCount - Param.jCount;
  } else {
    fpsDiff = localParam.fpsAverage - TARGET_FPS;
    if (fpsDiff > 10)
      deltaJellyfishCount = 10;
    else if (fpsDiff < -10)
      deltaJellyfishCount = -2;
    else {
      if (fpsDiff > 3)
        deltaJellyfishCount = Math.round(fpsDiff / 2);
      else if (fpsDiff < -3)
        deltaJellyfishCount = Math.round(fpsDiff / 4);
    }
    // sanity check
    if (deltaJellyfishCount + Param.jCount < 1) {
      Param.jCount = 1;
      deltaJellyfishCount = 0;
    }
    // If stable, we're done
    if (deltaJellyfishCount === 0 && lastDeltaJellyfishCount === 0 && lastLastDeltaJellyfishCount === 0) 
      reportResults(false);
    // if times up (20s), we're done
    if ((new Date().getTime() - startedTime) > 20000) {
      reportResults(true);
    }
    newCount = Param.jCount + deltaJellyfishCount;
  }
  Param.jCount = newCount;
}

function initWin(w, h) {
  var webglImplementationNames, nameIndex;
  (w) ? docWidth = w : docWidth = $(window).width();
  (h) ? docHeight = h : docHeight = $(window).height();
//  docWidth = Math.min(480, docWidth);
//  docHeight = Math.min(480, docHeight);
  var dPR = window.devicePixelRatio ? window.devicePixelRatio : 1.0;
  $("#webgl-canvas").width(docWidth);
  $("#webgl-canvas").height(docHeight);    
  canvas.width = docWidth * dPR;
  canvas.height = docHeight * dPR;
  webglImplementationNames = ["webgl", "experimental-webgl", "webkit-3d"];	// subset of list from khronos.org
  gl = null;
  for (var nameIndex = 0; nameIndex < webglImplementationNames.length; ++nameIndex) {
    try {
      gl = canvas.getContext(webglImplementationNames[nameIndex]);
    } catch(e) {}
    if (gl) {
      gl.viewportWidth = canvas.width;
      gl.viewportHeight = canvas.height;
      break;
    }
  }
}

function startTest() {
  if (!gl) {
    reportResults();
  } else {
    window.setInterval(updateCount, 2000);
    animate();
  }
}

$(window).resize(function() {
  initWin();
});

function webGLStart() {
  startedTime = new Date().getTime();

  canvas = document.getElementById("webgl-canvas");
  initWin();

  if (gl) {
    initBuffers();
    initShaders();
    initTextures();

    setDebugParam();

    gl.clearColor(0., 0., 0., 0.);
    gl.clearDepth(1.);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
    gl.enable(gl.BLEND);
    gl.enable(gl.DEPTH_TEST);
    gl.depthFunc(gl.LEQUAL);

    // Touch is disabled so we don't need this
    // interact();
  }
}
