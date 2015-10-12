/**
 * Copyright (c) 2014 Qualcomm Technologies, Inc.  All Rights Reserved.
 * Qualcomm Technologies Proprietary and Confidential.
 *
 * @preserve FrameCounter class for benchmarks
 */

var MS_TO_STABLE = 4000;
var WEIGHT_PREVIOUS_AVERAGE = 0.9;

function FrameCounter(samples) {
  this.minSamples = samples;
  this.clear();
}

FrameCounter.prototype.clear = function() {
  this.numFrames = 0;
  this.lastTimestamp = 0;
  this.firstSampleTime = 0;
  this.accumulatedError = 0;
  // Minimum time delta is likely the VSync time
  // Only intialize the current element for getLastTimeDelta
  this.lastTimeDelta = 0;
};

FrameCounter.prototype.isStable = function() {
  // FPS is considered stable if we have the minimum number of
  // samples, or if 4 seconds has elapsed since the first frame
  return ((this.numFrames >= this.minSamples)
      || ((Date.now() - this.firstSampleTime) >= MS_TO_STABLE));
};

FrameCounter.prototype.tick = function() {
  var now = Date.now();
  if (this.firstSampleTime == 0) {
    this.firstSampleTime = now;
  } else {
    // Get new time delta
    var newDelta = now - this.lastTimestamp;
    if (this.lastTimeDelta != 0) {
      var averageTimeDelta = this.getAverageTimeDelta();
      var normalizedDelta = (newDelta - averageTimeDelta) / averageTimeDelta;
      this.accumulatedError += normalizedDelta * normalizedDelta;
    }
    this.numFrames++;
    this.lastTimeDelta = newDelta;
  }
  this.lastTimestamp = now;
};

// Caller is responsible for checking if FPS is stable
// Avergae FPS is calculated by dividing the number of frames
// by the time delta between the last and the first sample time
FrameCounter.prototype.getAverageFps = function() {
  var elapsed = this.getLastTimeStamp() - this.firstSampleTime;
  // Return 0 if elapsed is less than one second
  if (this.numFrames == 0 || elapsed == 0) {
    return 0;
  }
  return (1000 * this.numFrames / elapsed);
};

// Caller is responsible for checking if FPS is stable
FrameCounter.prototype.getAverageTimeDelta = function() {
  if (this.numFrames == 0) {
    return 0;
  }
  var elapsed = this.getLastTimeStamp() - this.firstSampleTime;
  return (elapsed / this.numFrames);
};

FrameCounter.prototype.getLastFps = function() {
  if (this.lastTimeDelta == 0) {
    return 0;
  }
  return (1000 / this.lastTimeDelta);
};

FrameCounter.prototype.getLastTimeStamp = function() {
  return this.lastTimestamp;
};

FrameCounter.prototype.getLastTimeDelta = function() {
  return this.lastTimeDelta;
};

// Smoothness Mse normalized to the average time delta
FrameCounter.prototype.getSmoothnessMse = function() {
  if (this.numFrames == 0) {
    return 0;
  }
  return Math.sqrt(this.accumulatedError / this.numFrames);
};

FrameCounter.prototype.getNumFrames = function() {
  return this.numFrames;
};
