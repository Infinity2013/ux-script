/**
 * Copyright (c) 2014 Qualcomm Technologies, Inc.  All Rights Reserved.
 * Qualcomm Technologies Proprietary and Confidential.
 *
 * @preserve Helper class for converging numbers.
 */

// Converger class used to determine plus/minus delta of a tunable parameter until
// the target is reached.
// Note: Convergence is assumed to have happened only after the upper and lower
// bounds of the target range has been exceeded. For example, if a test starts out
// at target value already and stays on target, it is not considered to have converged.
// The convergence algorithm is linear (for now).

// target is the ideal KPI of the test. Note: Converger assumes that higher KPI is better.
// targetBufferPercent is the +/- percent within target considered to be more or less
//   reaching target. Range is (0.0, 1.0).
// maxIncrease is the max value to be added if performing better that target KPI
// maxDecrease is the max value to be reduced if performing worse than target KPI
//   It is recommended that maxIncrease and maxDecrease should not be the same number
//   and that they are not multiples of each other in order to converge to a wider
//   set of numbers. It is also recommended that one be odd and the other be even.
// convergeLimit is the number of entries at target where it is considered to have
//   reached steady state.
function Converger(target, targetBufferPercent, maxIncrease, maxDecrease, convergeLimit) {
  this.target = target;
  this.targetBufferPercent = targetBufferPercent;
  this.targetRangeMin = target * (1 - TARGET_BUFFER_PERCENT);
  this.targetRangeMax = target * (1 + TARGET_BUFFER_PERCENT);
  this.maxIncrease = maxIncrease;
  this.maxDecrease = maxDecrease;
  this.convergeLimit = convergeLimit;
  this.reset();
  this.calculateIncrease = function(actual) {
    var delta = 0;
    if (!this.hasDippedBelowTarget) {
      delta = this.maxIncrease;
    } else {
      var diff = actual - this.target;
      // If the diff is half of the target, set to maxIncrease
      // Otherwise, increase in proportion to how far off we are from delta
      delta = Math.round(this.maxIncrease * diff / (this.target / 2));
      // Cap at maxIncrease
      if (delta > this.maxIncrease)
        delta = this.maxIncrease;
    }
    return delta;
  }
  this.calculateDecrease = function(actual) {
    var delta = 0;
    if (!this.hasReachedOrExceededTarget) {
      delta = this.maxDecrease;
    } else {
      var diff = this.target - actual;
      // If the diff is half of the target, set to maxDecrease
      // Otherwise, decrease in proportion to how far off we are from delta
      delta = Math.round(this.maxDecrease * diff / (this.target / 2));
      // Cap at maxDecrease
      if (delta > this.maxDecrease)
        delta = this.maxDecrease;
    }
   return (delta * -1);
  }
}

Converger.prototype.reset = function() {
  this.hasDippedBelowTarget = false;
  this.hasReachedOrExceededTarget = false;
  this.results = [];
}

Converger.prototype.logAndGetDelta = function(actual) {
  var delta = 0;
  if (actual >= this.targetRangeMin)
    this.hasReachedOrExceededTarget = true;
  else
    this.hasDippedBelowTarget = true;

  if (actual >= this.targetRangeMin)
    delta = this.calculateIncrease(actual);
  else
    delta = this.calculateDecrease(actual);

  if (this.results.length >= this.convergeLimit) {
    // Pops the first element of the array
    this.results.shift();
  }
  this.results.push(delta);
  //console.log('results ' + this.results);
  return delta;
}

Converger.prototype.hasConverged = function() {
  if (this.results.length < this.convergeLimit)
    return false;

  if (!this.hasReachedOrExceededTarget || !this.hasDippedBelowTarget)
    return false;

  var i = this.results.length - 1;
  var plusDelta = this.calculateIncrease(this.targetRangeMax);
  var minusDelta  = this.calculateDecrease(this.targetRangeMin);
  while (i >= 0) {
    if (this.results[i] > plusDelta || this.results[i] < minusDelta )
      return false;
    --i;
  }
  return true;
}
