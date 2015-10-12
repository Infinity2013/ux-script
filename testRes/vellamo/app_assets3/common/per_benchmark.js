/**
 * Copyright (c) 2014 Qualcomm Technologies, Inc.  All Rights Reserved.
 * Qualcomm Technologies Proprietary and Confidential.
 *
 * @preserve Vellamo API for Benchmarks
 */

(function func(window, alert, console) {

  // API to use to communicate to the Shell
  window.VellamoBenchmark = {

    /* Debug level for each session.
        0:  none            (production)
        1:  debug on        (development)
    */
    debug : 0,

    /* Default refresh rate */
    maxRefreshRate : 60,

    /* Set to a function to be notified right after becoming worthless */
    onDisposeCallback : undefined,

    loadOnShellReady : function(initFunction) {
      Private.initCallback = initFunction;
      if (Private.inIframe === false) {
        Private.initCallback();
        return;
      }
      // Send a message to parent to continue
      window.parent.postMessage(
        {
          fromVellamoBenchmark : true,
          type : 'task-continue',
        }, '*'
      );
    },

    validRefreshRate : function(fps) {
      var FPS_TOLERANCE = 2.0;
      return (fps <= this.maxRefreshRate + FPS_TOLERANCE);
    },

    endWithResultsJSON : function(results) {
      results = Private.validateAndProcessResults(results);

      Private.checkAndSetEnded();
      if (Private.inIframe === false) {
        Private.showResultsLocally(results);
        return;
      }

      // communicate with the Vellamo Benchmark Shell (implicit Api)
      window.parent.postMessage(
        {
          fromVellamoBenchmark : true,
          type : 'benchmark-results',
          results: results,
          totalTimeMs : Private.msElapsed,
        }, '*'
      );
    },

    endWithError : function(userVisibleMessage, customErrorCode) {
      Private.checkAndSetEnded();
      if (Private.inIframe === false) {
        Private.showErrorLocally(userVisibleMessage);
        return;
      }

      // communicate with the Vellamo Benchmark Shell (implicit Api)
      window.parent.postMessage(
        {
          fromVellamoBenchmark : true,
          type : 'benchmark-error',
          userVisibleMessage : userVisibleMessage,
          customErrorCode : customErrorCode,
          totalTimeMs : Private.msElapsed,
        }, '*'
      );
    },

    endWithResultsAndMessage : function(results, userVisibleMessage) {
      Private.checkAndSetEnded();
      if (Private.inIframe === false) {
        Private.showErrorLocally(userVisibleMessage);
        return;
      }

      // communicate with the Vellamo Benchmark Shell (implicit Api)
      window.parent.postMessage(
        {
          fromVellamoBenchmark : true,
          type : 'benchmark-results-with-message',
          results: results,
          userVisibleMessage : userVisibleMessage,
          totalTimeMs : Private.msElapsed,
        }, '*'
      );
    },

  };


  // Shared functionality for Benchmarks
  // TODO
  // .. e.g. VellamoFpsMeasurer ..


  // Private API (removes weight from the VellamoBenchmark API)
  var Private = {
    inIframe :      window.parent !== window,
    alreadyEnded :  false,
    msInitial :     Date.now(),
    msElapsed :     0,
    initCallback :  null,

    swallowEvent : function(evt) {
      evt.preventDefault();
    },

    showResultsLocally : function(results) {
      var message = 'Standalone Benchmark Completed Succesfully.\nresults:  '+JSON.stringify(results, null, '  ');
      alert(message);
    },

    showErrorLocally : function(message) {
      alert('Standalone Benchmark Error Message: \n'+ message);
    },

    checkAndSetEnded : function() {
      if (Private.alreadyEnded === true) {
        Private._debugThrowApiError('calling the end function twice');
        return;
      }
      Private.msElapsed = Date.now() - Private.msInitial;
      Private.alreadyEnded = true;
    },

    validateAndProcessResults : function(r) {
      // ensure that R is an Object without prototype
      if (!(r.prototype === undefined && r instanceof Object)) {
        Private._debugThrowApiError('Results is not an object. Fix it.');
        return r;
      }
      // check every property in R for good behavior
      for (var key in r) {
        var value = r[key];
        if (typeof value == 'number') {
          // Number: valid.
        } else if (typeof value == 'string') {
          // String: valid if convertible to number -> Converted.
          var nValue = window.parseFloat(value);
          if (window.isNaN(nValue)) {
            Private._debugThrowApiError('Result property \''+key+'\' is a string ('+value+') and cannot be converted to a number. Fix it.');
            delete r[key];
          } else {
            Private._debugThrowApiError('Result property \''+key+'\' is a string ('+value+') which can be converted to number ('+nValue+'). Fix it.');
            r[key] = nValue;
          }
        } else if (value instanceof Array) {
          // Array: valid if array of Numbers -> Averaged.
          var isAllNumbers = true;
          var runningSum = 0;
          var runningElements = 0;
          value.forEach(function (element) {
            if (typeof element == 'number') {
              runningSum += element;
              runningElements ++;
            } else {
              isAllNumbers = false;
            }
          });
          if (isAllNumbers === true) {
            if (runningElements > 0) {
              r[key] = runningSum / runningElements;
            } else {
              Private._debugThrowApiError('Result property \''+key+'\' is an empty Array. Removing it.');
              delete r[key];
            }
          } else {
            Private._debugThrowApiError('Result property \''+key+'\' is a non-numeric Array. Removing it.');
            delete r[key];
          }
        } else {
          // Others: invalid.
          Private._debugThrowApiError('Result property \''+key+'\' is not of a supported type ('+typeof(value)+'). Removing it.');
          delete r[key];
        }
      }
      return r;
    },

    _debugThrowApiError : function(message) {
      if (VellamoBenchmark.debug === 1) {
        console.warn("Benchmark Api Error: "+message);
        throw "Benchmark Api Error: "+message;
      }
    },

    registerForShellMessages : function(handler) {
      if (window.addEventListener) {
        window.addEventListener("message", handler, false);
      } else {
        if (window.attachEvent)
          window.attachEvent("onmessage", handler);
        else {
          // NOTE/TODO: now what? we won't receive any message...
        }
      }
    },

    handleShellMessages : function(event) {
      // safety check
      var data = event.data;
      if (typeof data !== 'object' ||
          !('fromVellamoShell' in data) ||
          !('type' in data)) {
        // NOTE/TODO: Unrecognized message. Probably not from Vellamo Shell
        return;
      }

      // process the message from the shell
      switch (data.type) {
        case 'you-are-not-needed-anymore':
          // sent by shell to inform that the benchmark is closing
          if (typeof(window.VellamoBenchmark.onDisposeCallback) === 'function')
            window.VellamoBenchmark.onDisposeCallback();
          break;

        case 'max-refresh-rate':
          window.VellamoBenchmark.maxRefreshRate = data.message;
          if (VellamoBenchmark.debug === 1)
            console.log('max-refresh-rate ' + data.message);
          break;

        case 'init-callback':
          if (Private.initCallback)
            Private.initCallback();
          break;

        default:
          // NOTE/TODO: unhandled message
          break;
      }
    },

    disableTouchEvents : function() {
      window.addEventListener('mousedown', Private.swallowEvent, false);
      window.addEventListener('mouseover', Private.swallowEvent, false);
      window.addEventListener('mousemove', Private.swallowEvent, false);
      window.addEventListener('mouseup', Private.swallowEvent, false);
      window.addEventListener('click', Private.swallowEvent, false);
      window.addEventListener('touchstart', Private.swallowEvent, false);
      window.addEventListener('touchmove', Private.swallowEvent, false);
      window.addEventListener('touchend', Private.swallowEvent, false);
    },
  };

  // auto-register for shell messages
  Private.registerForShellMessages(Private.handleShellMessages);
  Private.disableTouchEvents();

  // query display max refresh rate from shell when ready to
  // receive messages
  window.parent.postMessage(
    {
      fromVellamoBenchmark : true,
      type : 'query-display-max-refresh-rate',
    }, '*'
  );
})(this, this.alert, this.console);
