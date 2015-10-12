// JavaScript Document
function getCurrentTime() {
  var frameRate;
  localParam.millis = new Date().getTime();
  localParam.timeNow = new Date().getTime();
  if (localParam.lastTime != 0) {
    localParam.elapsed = localParam.timeNow - localParam.lastTime;
    localParam.currentTime =localParam.millis%100000000 / 1000;
  }
  localParam.lastTime = localParam.timeNow;

  localParam.cycle32 = parseInt(localParam.currentTime*30 % 32 + 1);
  localParam.fps = 1000.0/localParam.elapsed;
  localParam.fpsAverage = (localParam.fpsAverage*9+localParam.fps)/10;
}

function tick(){
  getCurrentTime();
  setTimeUniform(localParam.currentTime);
}

//!!!
//var frameCountDown = 5;
//var stockJavascriptMathRandom = Math.random;
//var verypseudorandomnumber = 0;
//Math.random = function() {
//  verypseudorandomnumber += .1;
//  return (verypseudorandomnumber % 1);
//};
//function restoreStockJavascriptMathRandom() {
//	Math.random = stockJavascriptMathRandom;
//}
//!!!

function animate(){
//!!!
//  if (frameCountDown) {
//    var canvas = document.getElementById("webgl-canvas");
//    var gl = canvas.getContext('webgl', {preserveDrawingBuffer: true}) || canvas.getContext("experimental-webgl", {preserveDrawingBuffer: true});
//    tick();
//    drawScene();
//    var pixelSize = 4 * 480 * 480;
//    var pixelData = new Uint8Array(pixelSize);
//    gl.readPixels(0, 0, 480, 480, gl.RGBA, gl.UNSIGNED_BYTE, pixelData);
//    //Show what we captured
//    var debug = document.getElementById("webgl-debug");
//    if (!debug) {
//      debug = document.createElement('canvas');
//      debug.setAttribute("style", "position:absolute; left:480px; width:480px; height:480px; border: 1px solid #FFF;");
//      var body = document.getElementsByTagName("body")[0];
//      body.appendChild(debug);
//    }
//    var c2d = debug.getContext('2d');
//    var debugImage = c2d.createImageData(480, 480);
//    var r = debugImage.data;
//    for (i = 0; i < pixelSize; i += 4) {
//        r[i] = pixelData[i];
//        r[i+1] = pixelData[i+1];
//        r[i+2] = pixelData[i+2];
//        r[i+3] = 255;
//    }
//    c2d.putImageData(debugImage, 0, 0);
//    frameCountDown -= 1;
//    if (!frameCountDown) {
//      restoreStockJavascriptMathRandom();
//      //try to make more efficient by turning off preservation of buffer
//      gl = canvas.getContext('webgl', {preserveDrawingBuffer: false}) || canvas.getContext("experimental-webgl", {preserveDrawingBuffer: false});
//    }
//  }
//!!!
  requestAnimFrame( animate );
  tick();
  drawScene();
}

window.requestAnimFrame = (function(){
  return (
    window.requestAnimationFrame || 
    window.webkitRequestAnimationFrame   || 
    window.mozRequestAnimationFrame      || 
    window.oRequestAnimationFrame        || 
    window.msRequestAnimationFrame       || 
    function(/* function */ callback) { window.setTimeout(callback, 1000 / 60); }
  );
})();
