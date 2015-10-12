/**
 * Copyright (c) 2014 Qualcomm Technologies, Inc.  All Rights Reserved.
 * Qualcomm Technologies Proprietary and Confidential.
 *
 * @preserve Animation helper class for benchmarks
 */

//TODO:: Add unit test
function AnimationUtils() {
}

AnimationUtils.isRAFAvailable = true;
AnimationUtils.valid = true;

AnimationUtils.vellamoLog = function(input) {
  console.log(input);
}

// shim layer with setTimeout fallback
AnimationUtils.requestAnimFrame = function(callback){
  //Changed to support older IE browser
  if (window.requestAnimationFrame)
    window.requestAnimationFrame(callback);
  else if (window.webkitRequestAnimationFrame)
    window.webkitRequestAnimationFrame(callback);
  else if (window.mozRequestAnimationFrame)
    window.mozRequestAnimationFrame(callback);
  else if (window.oRequestAnimationFrame)
    window.oRequestAnimationFrame(callback);
  else if (window.msRequestAnimationFrame)
    window.msRequestAnimationFrame(callback);
  else {
    AnimationUtils.isRAFAvailable = false;
    window.setTimeout(callback, 1000 / 60);
  }
}

AnimationUtils.cancelLoop = function(callback) {
  return  window.cancelAnimationFrame(AnimationUtils.rAFHandle) ||
          window.mozCancelAnimationFrame(AnimationUtils.rAFHandle);
}

AnimationUtils.animLoop = function(animFunction) {
  function looper() {
    animFunction();
    AnimationUtils.rAFHandle = AnimationUtils.requestAnimFrame(looper);
    return AnimationUtils.rAFHandle;
  }
  handle = looper();
  return handle;
}

AnimationUtils.getDevicePixelRatio = function() {
  if (window.devicePixelRatio) {
    return window.devicePixelRatio;
  } else {
    console.log("Browser does not support devicePixelRatio");
    return 1.0;
  }
}

AnimationUtils.getBackingStoreRatio = function(context) {
  if (context.webkitBackingStorePixelRatio) {
    return context.webkitBackingStorePixelRatio;
  } else if (context.mozBackingStorePixelRatio) {
    return context.mozBackingStorePixelRatio;
  } else if (context.msBackingStorePixelRatio) {
    return context.msBackingStorePixelRatio;
  } else if (context.oBackingStorePixelRatio) {
    return context.oBackingStorePixelRatio;
  } else if (context.backingStorePixelRatio) {
    return context.backingStorePixelRatio;
  } else {
    console.log("Browser does not support BackingStorePixelRatio");
    return 1.0;
  }
}
