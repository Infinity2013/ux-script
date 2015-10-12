/**
 * Copyright (c) 2014 Qualcomm Technologies, Inc.  All Rights Reserved.
 * Qualcomm Technologies Proprietary and Confidential.
 *
 * @preserve Vellamo Shell: state machinery for Vellamo Browser
 *
 * @version 3.0
 * @codingstandard mixed
 * @assume jQuery 2
 */

/** TODO:
  investigate the 'console' object for a lot of debugging/tracing options
*/

(function(window) {
    'use strict';

    var $SD = {
        log : function(message) {
            console.log(/*'vellamo shell: '+*/message);
        },
        apiError : function(message, object) {
            if (!VellamoConsts.debug)
                return;
            console.error('API ERROR: ' + message);
            if (object !== undefined)
                console.warn(object);
        },
        notImplemented : function(message) {
            if (!VellamoConsts.debug)
                return;
            console.warn('vellamo shell: '+message+' is not implemented');
        },
    };


    var State = {
        // persistent
        benchmarkIDs : [],
        benchmarkIdx : -1,

        // implied
        spontaneous : false,

        // recreated
        benchmarks: [],
        benchmarkCount : 0,
        benchmarksRun : 0,


        parseFromRequest : function(request) {
            // TODO
        },

        _getQueryVariable : function(name) {
            var query = window.location.search.substring(1);
            var tokens = query.split('&');
            for (var n = 0; n < tokens.length; n++) {
                var pair = tokens[n].split('=');
                if (decodeURIComponent(pair[0]) === name)
                    return decodeURIComponent(pair[1]);
            }
            return undefined;
        },

        _parseQueryIntoConsts : function() {
            // ?repeat=3
            var qReps = this._getQueryVariable('repeat');
            if (qReps !== undefined && qReps >= 1)
                VellamoConsts.benchmarkSequenceRepetitions = qReps;

            // ?benchmarkId=vellamo.browser.CanvasAquarium
            var filterBenchmarkId = this._getQueryVariable('benchmarkId');
            if (filterBenchmarkId !== undefined) {
                for (var i = VellamoConsts.BenchmarkDescriptions.length; i--;) {
                    if (VellamoConsts.BenchmarkDescriptions[i].benchmarkId !== filterBenchmarkId) {
                        VellamoConsts.BenchmarkDescriptions.splice(i, 1);
                    }
                }
                VellamoConsts.benchmarkStartIndex = 0;
                VellamoConsts.benchmarkEndIndex = VellamoConsts.BenchmarkDescriptions.length;
            } else {
                //?start=2&end=5
                var startIndex = this._getQueryVariable('start');
                if (startIndex !== undefined) {
                    VellamoConsts.benchmarkStartIndex = parseInt(startIndex);
                }
                var endIndex = this._getQueryVariable('end');
                if (endIndex !== undefined) {
                    VellamoConsts.benchmarkEndIndex = parseInt(endIndex);
                }
            }
            if (VellamoConsts.benchmarkStartIndex === undefined) {
                VellamoConsts.benchmarkStartIndex = 0;
            }
            if (VellamoConsts.benchmarkEndIndex === undefined) {
                VellamoConsts.benchmarkEndIndex = VellamoConsts.BenchmarkDescriptions.length;
            }

            if (VellamoConsts.robustnessTests === undefined) {
                VellamoConsts.robustnessTests = [];
                VellamoConsts.robustnessTests.push(
                    {
                      benchmarkId :   'html5.debug.NeverLoad',
                      localizedName : 'NeverLoad',
                      localizedDesc : 'Robustness test for benchmark missing call to VellamoBenchmark.loadOnShellReady().',
                      shortDesc :     'Robustness test that never loads.',
                      location :      'test/neverload.html',
                      container :     'iframe',
                      operation :     'default',
                    });
                VellamoConsts.robustnessTests.push(
                    {
                      benchmarkId :   'html5.debug.NeverComplete',
                      localizedName : 'NeverComplete',
                      localizedDesc : 'Robustness test for benchmark missing call to VellamoBenchmark.endWithResults() or endWithError().',
                      shortDesc :     'Robustness test that never ends.',
                      location :      'test/nevercomplete.html',
                      container :     'iframe',
                      operation :     'default',
                    });
            }
        },

        _insertRobustnessTests: function() {
          var position;

          for (var i = 0; i < VellamoConsts.robustnessTests.length; i++) {
            // Generate random index between min and max values
            position = Math.floor(Math.random() * (State.benchmarks.length + 1));
            // Insert into State.benchmarkIdx at position
            State.benchmarks.splice(position, 0, VellamoConsts.robustnessTests[i]);
          }
        },

        initSpontaneous : function() {
            this._parseQueryIntoConsts();

            this.benchmarkIdx = -1;
            this.spontaneous = true;
            this.benchmarksRun = 0;

            switch (VellamoConsts.spontaneousOperation) {
                case 'blank': break;

                case 'countdown':
                    // fall through - countdown leads to autosequence
                case 'autoSequence':
                    var repetitions = VellamoConsts.benchmarkSequenceRepetitions || 1;
                    var sessionBenchmarks = VellamoConsts.BenchmarkDescriptions.slice(VellamoConsts.benchmarkStartIndex, VellamoConsts.benchmarkEndIndex);
                    for (var n = 0; n < repetitions; n++) {
                        sessionBenchmarks.forEach(function(benchmarkDesc) {
                            State.benchmarkIDs.push(benchmarkDesc.benchmarkId);
                        });
                    }
                    break;
                case 'benchmarkChooser': break;
                case 'random10':
                    for (var i = 0; i < 10; ++i) {
                        var idx = Math.floor(Math.random()*(VellamoConsts.benchmarkEndIndex - VellamoConsts.benchmarkStartIndex));
                        State.benchmarkIDs.push(VellamoConsts.BenchmarkDescriptions[VellamoConsts.benchmarkStartIndex + idx].benchmarkId);
                    }
                    break;
                default:
                    $SD.apiError('spontaneousOp of type '+VellamoConsts.spontaneousOperation+' are not implemented');
                    break;
            }
        },

        // generate the redundant (and helpful) state information
        genRemainingState : function() {
            // populate the benchmarks array from the templates in the configuration
            var sessionBenchmarks = VellamoConsts.BenchmarkDescriptions.slice(VellamoConsts.benchmarkStartIndex, VellamoConsts.benchmarkEndIndex);
            this.benchmarkIDs.forEach(function(benchmarkId) {

                // find the right match in the descriptions
                for (var descIndex = 0; descIndex < sessionBenchmarks.length; ++descIndex) {
                    var benchmarkDesc = sessionBenchmarks[descIndex];
                    if (benchmarkDesc.benchmarkId !== benchmarkId)
                        continue;

                    // clone the object
                    var benchmark = {
                        benchmarkId :   benchmarkDesc.benchmarkId,
                        localizedName : benchmarkDesc.localizedName,
                        localizedDesc : benchmarkDesc.localizedDesc,
                        shortDesc :     benchmarkDesc.shortDesc,
                        location :      benchmarkDesc.location,
                        container :     benchmarkDesc.container,
                        operation :     benchmarkDesc.operation,
                    };

                    // resolve the right location
                    if (VellamoConsts.benchmarkPrefix !== '')
                        benchmark.location = VellamoConsts.benchmarkPrefix + benchmark.location;

                    // enlist
                    State.benchmarks.push(benchmark);

                    // found it
                    break;
                }
            });
            if (VellamoConsts.debug >= 2) {
              this._insertRobustnessTests();
              this.benchmarkCount += VellamoConsts.robustnessTests.length;
            }
            // update total count
            this.benchmarkCount = State.benchmarks.length;
        },
        updateProgressBar : function () {
            var benchmarkTotalCount;
            var benchmarksDone = State.benchmarksRun;
            if (VellamoConsts.progressBarCount) {
              benchmarksDone += VellamoConsts.progressBarStart;
              benchmarkTotalCount = VellamoConsts.progressBarCount;
            } else {
              benchmarkTotalCount = State.benchmarks.length;
            }
            if (VellamoConsts.debug >= 1)
                $SD.log("benchmarksDone="+benchmarksDone+", benchmarkTotalCount="+benchmarkTotalCount);
            var newWidthPercent = benchmarksDone * 100 / benchmarkTotalCount;
            var bar = document.getElementById('vs_progress_bar');
            bar.style.width = newWidthPercent + "%";
        },
        reset : function() {
            State.benchmarksRun = 0;
        },
        benchmarkDone: function() {
            // ... and update progress bar
            State.benchmarksRun += 1;
            State.updateProgressBar();
        },
    };

    function ResultMessage() {
        this.duration = 0;
        this.benchmarkLoadTime = 0;
        this.benchmarkId = '';
        this.results = {};
        this.errorCode = undefined;
        this.errorMessage = undefined;
        this.computeScore = function() {
			// Setup the 'r' object from JSON
			var mCode = "var r; try { r = { ";
			var firstValue = true;
			for (var rawName in this.results) {
				var rawValue = this.results[rawName];
				if (!firstValue)
					mCode += ", ";
				else
					firstValue = false;
				mCode += "\""+rawName+"\": "+rawValue;
			}
			mCode += " }; ";

			// output the result of the computation
			mCode += "("+VellamoConsts.BenchmarkLookup[this.benchmarkId].scoreFormula+");";

			// try to intercept errors in the console message
			mCode += "} catch(e) { console.log(''+e); 0; } ";

			this.score = eval(mCode);
        };
    }

    function Task(name, machine, asyncRunFunction) {
        var me = this;
        this.name = name;
        this.watchdogMs = 120000;
        this.watchdogHandle;
        this.watchdogStart;
        this.runTaskAsync = asyncRunFunction || function() {
            $SD.apiError('runTaskAsync not re-implemented for task '+name+'. Continuing.', this);
            this.taskDone();
        };
        this.taskDone = function() {
            clearTimeout(this.watchDogHandle);
            machine._taskDone(me);
        };

        this.startWatchdog = function() {
            if (VellamoConsts.debug > 1)
              this.watchdogStart = Date.now();
            this.watchDogHandle = setTimeout(function() {
                if (VellamoConsts.browserImageName === null) {  //If Vellamo is driving, let it handle timeouts
                  TaskMachine.watchdogExpired(me);
                }
            }, this.watchdogMs);
        };
    }

    var TaskMachine = {
        // NOTE: Should make: Landing, GenState, Greet, ((B_LoadNext, B_Swap, B_Start, B_End)), Exception (timeout, code_error, user_interaction, system_unstable,...)
        paused : true,

        taskList : [],
        taskCount : 0,
        taskIndex : -1,
        taskAtEnd : true,
        taskCurrent : undefined,

        nextTaskTimerId : undefined,

        append : function(task) {
            if (task.runTaskAsync === undefined) {
                $SD.apiError('TaskMachine: the task '+task.name+' is missing the runTaskAsync function');
                return;
            }
            this.taskList.push(task);
            var wasAtEnd = this.taskAtEnd;
            this.taskCount++;
            this.taskAtEnd = false;
            if (this.paused === false && wasAtEnd === true)
                this._schedNextTask(1);
        },

        resume : function() {
            if (this.paused === false)
                return;
            this.paused = false;
            this._schedNextTask(0);
        },

        emptyLeaveRunning : function() {
            this.taskList = [];
            this.taskCount = 0;
            this.taskIndex = -1;
            this.taskAtEnd = true;
            this.taskCurrent = undefined;
            if (this.nextTaskTimerId !== undefined) {
                clearTimeout(this.nextTaskTimerId);
                this.nextTaskTimerId = undefined;
            }
        },

        /*pause : function() {
            if (this.paused === true)
                return;
            this.paused = true;
        },*/

        _isTaskAtEnd : function () {
            var atEnd = (this.taskIndex >= (this.taskCount - 1));
            return atEnd;
        },

        _nextTask : function() {
            if (this.taskCurrent !== undefined) {
                $SD.apiError('TaskMachine: calling _nextTask with the former still pending');
                return;
            }

            if (this.paused === true) {
                $SD.apiError('TaskMachine: calling _nextTask with task machine paused');
                return;
            }

            this.taskAtEnd = this._isTaskAtEnd();
            if (this.taskAtEnd === true) {
                if (VellamoConsts.debug >= 1)
                    $SD.log('executed all');
                return;
            }

            this.taskIndex++;
            this.taskCurrent = this.taskList[this.taskIndex];

            if (VellamoConsts.debug >= 1)
                $SD.log('Task '+this.taskCurrent.name+' starting... ');

            this.taskCurrent.startWatchdog();
            this.taskCurrent.runTaskAsync();
        },

        _taskDone : function(task) {
            // sanity (in-order) check
            if (task !== this.taskCurrent) {
                $SD.apiError('Task done, but not the most current one! Skipping.', task);
                return;
            }
            this.taskCurrent = undefined;

            if (VellamoConsts.debug >= 1)
                $SD.log('Task '+task.name+' done.');

            if (this.paused === true) {
                $SD.log('Task machine is paused. Not Advancing');
                return;
            }

            this._schedNextTask(1);
        },

        _schedNextTask : function(ms) {
            if (this.nextTaskTimerId !== undefined)
                clearTimeout(this.nextTaskTimerId);
            this.nextTaskTimerId = setTimeout(function() {
                TaskMachine.nextTaskTimerId = undefined;
                TaskMachine._nextTask();
            }, ms || 100);
        },

        watchdogExpired : function(task) {
          if (VellamoConsts.debug >= 1)
            $SD.log('Watchdog expired after ' + (Date.now() - task.watchdogStart) + ' seconds! Ending ' + task.name + ' task.');

          var output = new ResultMessage();
          output.duration = task.watchdogMs;
          output.errorCode = 'DEAD';
          output.errorMessage = 'Watchdog timer expired';

          // If this is the preloader, skip next task
          // Assumes next task is the run benchmark task
          if (task.name === 'preloader') {
            // Compute the actual benchmarkLoadTime.
            // The start time should already be set in benchmarkLoadTime.
            SurfaceLayouter.pendingIFrameElement.benchmarkLoadTime =
                  Date.now() - SurfaceLayouter.pendingIFrameElement.benchmarkLoadTime;
            // Force transition done
            TaskMachine.transitionDone();
            if (VellamoConsts.debug >= 1)
              $SD.log('Preloader failed. Skipping benchmark ' + task.theBenchmark.benchmarkId);
            TaskMachine.skipNextBenchmarkTask();
          }

          if (SurfaceLayouter.iFrameElement)
            output.benchmarkLoadTime = SurfaceLayouter.iFrameElement.benchmarkLoadTime / 1000;

          if (TaskMachine.taskCurrent.theBenchmark !== undefined) {
            output.benchmarkId = TaskMachine.taskCurrent.theBenchmark.benchmarkId;
            // now store the output and send it to Vellamo
            TaskMachine.taskCurrent.theBenchmark.output = output;
          }

          AppComm.sendOutput(output);
          // Advance benchmark and mark task done
          State.benchmarkDone();
          task.taskDone();
        },

        skipNextBenchmarkTask: function() {
            // Assumes that Preloader is immediately followed by a Run task
            if (!this._isTaskAtEnd()) {
                this.taskIndex++;
            }
        },

        _loadBenchmark : function (b) {
            if (b.container !== 'iframe') {
                $SD.notImplemented('We only support iframes for now, not '+b.container);
                task.taskDone();
                return;
            }
            SurfaceLayouter.createEmbeddedIFrame();
            if (VellamoConsts.debug >= 1)
              $SD.log('Loading benchmark ' + b.location);

            var location = b.location;
            if (VellamoConsts.hackAppendLocationQueries)
                location = location+'?'+Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);

            // Save the load start time
            SurfaceLayouter.pendingIFrameElement.benchmarkLoadTime = Date.now();
            SurfaceLayouter.runOnIFrame(location);
        },

        transitionDone: function() {
          if (SurfaceLayouter.iFrameElement)
            SurfaceLayouter.resetContainer(SurfaceLayouter.iFrameElement);
          BenchmarkMessageHub.sendMessageToIFrame(SurfaceLayouter.pendingIFrameElement, 'init-callback');
          SurfaceLayouter.iFrameElement = SurfaceLayouter.pendingIFrameElement;
        },

        make_T_Benchmark : function(b) {
            var task = new Task('run '+b.benchmarkId, TaskMachine);
            task.theBenchmark = b;
            task.runTaskAsync = function() {
                if (SurfaceLayouter.iFrameElement)
                  BenchmarkMessageHub.sendMessageToIFrame(SurfaceLayouter.iFrameElement, 'you-are-not-needed-anymore');

                State.updateProgressBar();
                setTimeout(function() {
                    SurfaceLayouter.transitionToNextBenchmark();
                    $('#vs_topbar_info_name').fadeOut(200, function() {
                       $('#vs_topbar_info_name').html(b.localizedName).show();
                    });

                    if (VellamoConsts.showDescriptions)
                        $('#vs_topbar_info_description').text(SurfaceLayouter.isLargeScreen ? b.localizedDesc : b.shortDesc);
                }, 400);
            };
            return task;
        },

        make_T_Preloader : function(nextBenchmark) {
            var task = new Task('preloader', TaskMachine);
            task.theBenchmark = nextBenchmark;
            task.runTaskAsync = function() {
                if (nextBenchmark !== null) {
                  TaskMachine._loadBenchmark(nextBenchmark);
                } else {
                  task.taskDone();
                  return;
                }
            };
            return task;
        },
    };


    var SurfaceLayouter = {
        initialized : false,
        bodyAfterStyleRef : undefined,
        isPortrait : undefined,
        isLargeScreen : undefined,

        iFrameElement : undefined,
        pendingIFrameElement: undefined,
        styleTopBar : undefined,
        styleContent : undefined,

        contentSize : 0,
        contentMarginLeft : 0,
        contentMarginTop : 0,
        lastUsed: 'pong',

        onSurfaceChanged : function (event) {
            if (event.type !== 'resize')
                $SD.log('NON-RESIZE EVENT, YEY');
            switch (VellamoConsts.surfaceChange) {
                case 'keepinitial': /* don't do any further update when size changes */ break;
                case 'relayout': SurfaceLayouter.doRelayout.call(SurfaceLayouter); break;
                case 'reorient': SurfaceLayouter.doReorient.call(SurfaceLayouter); break;
                // TODO: on relayout and reorient, should post a task to do the adjustment
            }
        },

        resetContainer: function(e) {
          var id = this.iFrameContainerId(e.suffixId);
          $('#' + id).addClass('vs-hidden');
          $('#' + id).removeClass('vs-content-slide-out vs-content-slide-in');
          $('#' + id).empty();
        },

        _initialize : function() {
            if (window.getComputedStyle !== undefined) {
                this.bodyAfterStyleRef = window.getComputedStyle(document.body, ":after");
            }
            this.styleTopBar = this._initializeElement('vs_topbar');
            this.styleContent = this._initializeElement('vs_content');
            if (VellamoConsts.browserImageName) {
                var browserIcon = document.getElementById('vs_browser_icon');
                browserIcon.innerHTML = '<img src="shell/img/' + VellamoConsts.browserImageName+'" style="width : 16px; height : 16px;">';
                var style = browserIcon.style;
                style.display = 'inline';
                style.height = "16px";
                style.width = "16px";
                $('#vs_browser_label').text('-Browser');
            }
            this.initialized = true;
        },

        _initializeElement : function(id, styleRef) {
            var element = document.getElementById(id);
            element.className = '';
            var style = element.style;
            style.position = 'absolute';
            return style;
        },

        readOrientation : function() {
            this.isPortrait = undefined;
            this.isLargeScreen = undefined;

            //One line work-around for KK WebView follows...
            if (!($(window).height() === 0) && window.matchMedia) {
                // portrait vs. landscape detection
                if (window.matchMedia("(orientation: portrait)").matches === true)
                    this.isPortrait = true;
                else if (window.matchMedia("(orientation: landscape)").matches === true)
                    this.isPortrait = false;
                // heuristic large vs. small screen detection
                if (this.isPortrait === false && window.matchMedia("(min-width: 1224px)").matches === true)
                    this.isLargeScreen = true;
            }

            // first try to parse with Media Query
            if (this.bodyAfterStyleRef !== undefined) {
                var letter = this.bodyAfterStyleRef.content+'';
                if (letter.indexOf('p') > -1) { this.isPortrait = true; }
                else if (letter.indexOf('l') > -1) { this.isPortrait = false; }
            }

            // then try to use the aspect ratio of the window
            if (this.isPortrait === undefined)
                this.isPortrait = window.innerWidth <= window.innerHeight;

            // assume it's a small debvice if media queries are not supported
            if (this.isLargeScreen === undefined)
                this.isLargeScreen = false;
        },

        doReorient : function() {
            if (this.initialized === false)
                this._initialize();
            this.readOrientation();
            this.doRelayout();
        },

        _setGeometry : function(style, l, t, w, h) {
            style.left = l+'px';
            style.top = t+'px';
            style.width = w+'px';
            style.height = h+'px';
        },

        doRelayout : function() {
            if (this.isPortrait === undefined) {
                $SD.apiError('SurfaceLayouter.doRelayout called without a set orientation');
                return;
            }

            var W = $(window).width();
            var H = $(window).height();
            //Three line work-around for KK WebView follows...
            if (H === 0) {
                H = window.innerHeight;
            }

            // Layout needs to be completely changed! This is an initial algo
            var maxSide = W > H ? W : H;
            var minSide = W < H ? W : H;
            var padding = 0;

            // For screens that are close to being a square, guarantee that
            // 1/4 of the screen space can be used for the header
            if (minSide > maxSide * 3 / 4) {
                minSide = Math.round(maxSide * 3 / 4);
                padding = 0;
            }
            var headerSize = maxSide - minSide;
            this.contentSize = minSide - padding;

            if (this.isPortrait === true) {
                var left = 0;
                var width = W;
                this._setGeometry(this.styleTopBar, left, 0, width, headerSize);
                this._setGeometry(this.styleContent, left, headerSize, width, minSide);
                this.contentMarginLeft = Math.floor((width - this.contentSize) / 2);
                this.contentMarginTop = 0;
            } else {
                var top = 0;
                var height = H;
                this._setGeometry(this.styleTopBar, 0, top, headerSize, height);
                this._setGeometry(this.styleContent, headerSize, top, minSide, height);
                this.contentMarginLeft = 0;
                this.contentMarginTop = Math.floor((height - this.contentSize) / 2);
            }

            if (this.iFrameElement !== undefined)
                this._setGeometry(this.iFrameElement.style, this.contentMarginLeft, this.contentMarginTop, this.contentSize, this.contentSize);
        },

        _toggleIFrameId : function() {
            if (this.lastUsed === 'ping')
              this.lastUsed = 'pong';
            else
              this.lastUsed = 'ping';
            return this.lastUsed;
        },

        iFrameId: function(suffix) {
            return 'vs_content_iframe_container_' + suffix;
        },

        iFrameContainerId : function(suffix) {
            var id = 'vs_content_iframe_container_' + suffix;
            return id;
        },

        transitionToNextBenchmark : function() {
          if (this.iFrameElement) {
            // Slide out the current benchmark
            var id = this.iFrameContainerId(this.iFrameElement.suffixId);
            // This animation listener doesn't seem to be working
            //$('#' + id).on('webkitTransitionEnd oTransitionEnd msTransitionEnd transitionend',
            //    TaskMachine._onAnimationEnded);
            $('#' + id).addClass('vs-content-slide-out');
          }

          if (this.pendingIFrameElement) {
            // Compute the actual benchmarkLoadTime.
            // The start time should already be set in benchmarkLoadTime.
            SurfaceLayouter.pendingIFrameElement.benchmarkLoadTime =
                Date.now() - SurfaceLayouter.pendingIFrameElement.benchmarkLoadTime;
            // Slide in the new benchmark
            var id = this.iFrameContainerId(this.pendingIFrameElement.suffixId);
            $('#' + id).addClass('vs-content-slide-in').removeClass('vs-hidden vs-content-slide-out');
          }
          setTimeout(TaskMachine.transitionDone, 1067);
        },

        createEmbeddedIFrame : function() {
            // create and style a new iframe
            this.pendingIFrameElement = document.createElement('iframe');
            this.pendingIFrameElement.suffixId = this._toggleIFrameId();
            this.pendingIFrameElement.className = "vs-content-iframe";

            if (VellamoConsts.debug >= 1)
                this.pendingIFrameElement.style.background = 'red';

            // add pendingIFrameElement to the document
            var container = this.iFrameContainerId(this.pendingIFrameElement.suffixId);
            var parent = document.getElementById(container);
            if (!parent) {
              // The parent div may not present if this is the first time loading the
              // benchmarks or if we are jumping to a benchmark from the results page
              this._initIFrameContainers();
              parent = document.getElementById(container);
            }
            $('#' + container).empty();
            $('#' + container).addClass('vs-hidden');
            parent.appendChild(SurfaceLayouter.pendingIFrameElement);

            // reposition the iframe immediately
            this._setGeometry(this.pendingIFrameElement.style, this.contentMarginLeft, this.contentMarginTop, this.contentSize, this.contentSize);
        },

        stopEmbeddedIFrame : function() {
            window.frames[0].stop();
        },

        runOnIFrame : function(url) {
            // sanity check
            if (this.pendingIFrameElement === undefined) {
                SurfaceLayouter.setContentInlineError('No IFrame');
                $SD.apiError('The content iframe has not been created.');
                return;
            }
            // start the loading process. from here on, we have to 'assume' that it will work
            this.pendingIFrameElement.src = url;
        },

        resetContent: function() {
          $('#vs_content').removeClass().empty();
          SurfaceLayouter.pendingIFrameElement = undefined;
          SurfaceLayouter.iFrameElement = undefined;
          SurfaceLayouter.setContentBackgroundColor('initial');
        },

        setContentBackgroundColor : function(color) {
            $('#vs_content').css('background-color', color);
        },

        _initIFrameContainers : function() {
            $('#vs_content').append('<div id="vs_content_iframe_container_ping" class="vs-content-iframe-container">');
            $('#vs_content').append('<div id="vs_content_iframe_container_pong" class="vs-content-iframe-container">');
        },

        setContentInlineMessage : function(message) {
            $('#vs_content').html('<div style="text-align: center"><br/>'+message+'</div>');
            $('#vs_content').addClass('vs-selectable');
        },

        setContentInlineError : function(error) {
            $('#vs_content').html('<div style="text-align: center; color: darkred; font-size: 1.6em;"><br/>'+error+'</div>');
            $('#vs_content').addClass('vs-selectable');
        },

        /*setContentInlineURL : function(url) {
            // handle the no-page case
            if (url === null || url === "") {
                SurfaceLayouter.setContentInlineError('invalid content url.');
                // TODO: and then what?
                return;
            }

            // start the load operation
            $('#vs_content').load(url, SurfaceLayouter._loadResponseParser);
        },

        _loadResponseParser : function(response, status, xhr) {
            switch (status) {
                case 'error':
                    SurfaceLayouter.setContentInlineError('error dynloading the content');
                    // TODO: and then what?
                    break;
                case 'success':
                    break;
                default:
                    $SD.notImplemented('Response for Status '+status);
                    break;
            }
        },*/
    };


    var BenchmarkMessageHub = {
        register : function() {
            if (window.addEventListener) {
                window.addEventListener("message", BenchmarkMessageHub.receive, false);
            } else {
                if (window.attachEvent)
                    window.attachEvent("onmessage", BenchmarkMessageHub.receive);
                else {
                    alert('This Browser does not support Message Passing between IFrames.');
                    // TODO: now what? signal it to the user / to Vellamo
                }
            }
        },

        sendMessageToIFrame: function(iframe, type, message) {
          if (!iframe) {
            $SD.apiError('No IFrames to send the message to', message);
            return;
          }
          if (!iframe.contentWindow) {
            // This could happen in debug mode if jumping around from one benchmark
            // to another before it has a chance to load
            $SD.apiError('IFrame has no content window');
            return;
          }
          iframe.contentWindow.postMessage(
              {
                fromVellamoShell : true,
                type : type,
                message : message,
              }, '*'
            );
        },

        sendMessageToBenchmarkBlindly : function(type, message) {
            // sanity check
            if (window.frames.length !== 1) {
                $SD.apiError('No IFrames to send the message to', message);
                return;
            }
            // send a message to the iFrame, which is handled in 'per_benchmark.js'
            var iFrame = window.frames[0];
            iFrame.postMessage(
              {
                fromVellamoShell : true,
                type : type,
                message : message,
              }, '*'
            );
        },

        receive : function(event) {
            // safety check
            var data = event.data;
            if (typeof data !== 'object' ||
                    !('fromVellamoBenchmark' in data) ||
                    !('type' in data)) {
                $SD.apiError('Unrecognized message. Probably not from a Vellamo Benchmark. Data:', data);
                return;
            }

            // sanity check
            if (TaskMachine.taskCurrent === undefined) {
                AppComm.shellError('Got Benchmark Result, but Task is gone.');
                return;
            }

            // store the results of the benchmark execution
            var output = new ResultMessage();

            // process the message from the benchmark
            switch (data.type) {
                case 'benchmark-results':
                    if (TaskMachine.taskCurrent.theBenchmark === undefined) {
                        AppComm.shellError('Got Benchmark Result, but Task is not a benchmark one.');
                        return;
                    }
                    output.duration = data.totalTimeMs / 1000;
                    if (SurfaceLayouter.iFrameElement)
                       output.benchmarkLoadTime = SurfaceLayouter.iFrameElement.benchmarkLoadTime / 1000;
                    output.benchmarkId = TaskMachine.taskCurrent.theBenchmark.benchmarkId;
                    output.results = data.results;
                    break;
                case 'benchmark-error':
                    if (TaskMachine.taskCurrent.theBenchmark === undefined) {
                        AppComm.shellError('Got Benchmark Result, but Task is not a benchmark one.');
                        return;
                    }
                    output.duration = data.totalTimeMs / 1000;
                    if (SurfaceLayouter.iFrameElement)
                       output.benchmarkLoadTime = SurfaceLayouter.iFrameElement.benchmarkLoadTime / 1000;
                    output.benchmarkId = TaskMachine.taskCurrent.theBenchmark.benchmarkId;
                    output.errorCode = data.customErrorCode;
                    output.errorMessage = data.userVisibleMessage;
                    break;
                case 'benchmark-results-with-message':
                    if (TaskMachine.taskCurrent.theBenchmark === undefined) {
                        AppComm.shellError('Got Benchmark Result, but Task is not a benchmark one.');
                        return;
                    }
                    output.duration = data.totalTimeMs / 1000;
                    if (SurfaceLayouter.iFrameElement)
                       output.benchmarkLoadTime = SurfaceLayouter.iFrameElement.benchmarkLoadTime / 1000;
                    output.benchmarkId = TaskMachine.taskCurrent.theBenchmark.benchmarkId;
                    output.results = data.results;
                    output.errorMessage = data.userVisibleMessage;
                    break;
                case 'query-display-max-refresh-rate':
                    if (TaskMachine.taskCurrent.theBenchmark === undefined)
                      return;
                    if (SurfaceLayouter.pendingIFrameElement) {
                      BenchmarkMessageHub.sendMessageToIFrame(SurfaceLayouter.pendingIFrameElement,
                        'max-refresh-rate', VellamoConsts.maxRefreshRate);
                    }
                    output = undefined;
                    break;
                case 'task-continue':
                    // sent by non-benchmark tasks to continue
                    output = undefined;
                    break;
                default:
                    $SD.apiError('BenchmarkMessageHub.receive: unhandled message of type '+data.type+'. continuing');
                    break;
            }

            // now store the output and send it to Vellamo
            if (output !== undefined) {
                TaskMachine.taskCurrent.theBenchmark.output = output;
                AppComm.sendOutput(output);
                // ... and update progress bar
                State.benchmarksRun += 1;
                State.updateProgressBar();
            }

            /* if not a query message, advance the task machine */
            if ((data.type).indexOf("query") == -1) {
              // advance the Task Machine (which was supposedly waiting for a benchmark task to end)
              TaskMachine.taskCurrent.taskDone();
            }
        },
    };

    var AppComm = {
        sendOutput : function(output) {
            var jsonURL = encodeURIComponent(JSON.stringify(output));
            var payload = jsonURL + ',' + new Date().getTime();
            AppComm._callWebServer('result.test', payload);
        },
        shellError : function(error) {
            // NOTE: the following is not yet implemented
            //AppComm._callWebServer('error.test', encodeURIComponent(JSON.stringify(error)));
        },
        shellAbort : function() {
            AppComm._callWebServer('result.test', encodeURIComponent("{abort:true}"));
        },
        sendStateInformation : function(tbd) {
            // NOTE: the following is not yet implemented
            //$SD.notImplemented('Appcomm.sendStateInformation '+tbd);
        },

        _callWebServer : function(page, payload) {
            // Async request; assumes the Vellamo web server will handle the message
            // handles errors too (e.g. web server not running)
            $.ajax(page + '?' + payload)
            .done(function() {
                // NOTE: Vellamo has been notified about the score
            })
            .fail(function(req, text, error) {
                // We failed the request
                if (VellamoConsts.browserImageName !== null) {
                    // We are driven by Vellamo, but Vellamo doesn't respond
                    $SD.log("Reporting result to Vellamo failed: "+text+" (page: "+page+", error: "+error+")");

                    // clear the body
                    $('body').css('display', 'none');
                    $('body').html(
                        "<div id='vs_thankyou_container'>" +
                        " <div class='vs-thankyou'>" +
                        "  <div class='vs-thankyou-title'>" +
                        "    Stopped." +
                        "  </div>" +
                        "  <div class='vs-thankyou-content'>" +
                        "    Cannot communicate with the Vellamo APP.<br>" +
                        "    Sometimes when the browser uses too much memory, the system may close the Vellamo APP.<br>" +
                        "    <br>" +
                        "    You can <a href='javascript:window.open(\"\",\"_self\").close();' style='text-decoration: underline; color: #888'>close this tab</a> now and try again.<br>" +
                        "  </div>" +
                        " </div>" +
                        "</div>"
                    );
                    $('body').fadeIn(1000);
                } else {
                    // We are in the Web interface
                    // TODO: do something here?
                }
            });
        },
    };


    function onDocumentReady() {
        // do it once, unless relayouting later
        TaskMachine.append(new Task('reorient', TaskMachine,
            function() {
                SurfaceLayouter.doReorient.call(SurfaceLayouter);
                this.taskDone();
            }
        ));
        // test if our session is still active
        if (VellamoConsts.benchmarkPrefix.length === 0) {
            $.ajax('shell/img/vs_fav16.png?' + new Date().getTime())
            .done(function() {
                sessionOk();
            })
            .fail(function() {
                // nothing we can do, go somewhere else
                window.location.href = "http://www.google.com/";
            });
        } else {
            sessionOk();
        }
    }
    function sessionOk() {
        // parse persistent state, generate the rest
        var request = undefined;
        if (request === undefined)
            State.initSpontaneous();
        else
            State.parseFromRequest(request);
        State.genRemainingState();

        // if we activated countdown, add it first here
        if (State.spontaneous === true && VellamoConsts.spontaneousOperation === 'countdown') {
            var benchmark = {
                    benchmarkId :   'vellamo.browser.countdown',
                    localizedName : 'Countdown',
                    location :      'shell/scenes/countdown.html',
                    container :     'iframe',
                    operation :     'default',
                };
            TaskMachine.append(TaskMachine.make_T_Preloader(benchmark));
            TaskMachine.append(TaskMachine.make_T_Benchmark(benchmark));
        }

        // if benchmarks are queued, create execution Tasks for them
        var queuedBenchmarks = 0;
        for (var j = State.benchmarkIdx + 1; j < State.benchmarkCount; j++) {
            var benchmark = State.benchmarks[j];
            TaskMachine.append(TaskMachine.make_T_Preloader(benchmark));
            TaskMachine.append(TaskMachine.make_T_Benchmark(benchmark));
            if (j == State.benchmarkCount - 1)
              TaskMachine.append(TaskMachine.make_T_Preloader(null));
            queuedBenchmarks++;
        }

        // handle more beginning scenarios
        if (State.spontaneous === true) {
            switch (VellamoConsts.spontaneousOperation) {
                case 'blank':
                    SurfaceLayouter.setContentInlineMessage('blank.');
                    break;

                case 'countdown':
                    // already pre-handled in this same function
                    break;

                //case 'benchmarkChooser': break;

                case 'autoSequence': break;
                case 'random10': break;

                default:
                    $SD.apiError('spontaneousOperation of type '+VellamoConsts.spontaneousOperation+' is not implemented');
                    break;
            }
        } else {
            if (queuedBenchmarks < 1) {
                $SD.apiError('Non-spontaneous operation but no queued benchmarks. Ending?');
                AppComm.shellError('', 1);
                // TODO: migrate to an end exit/error state?
            }
        }

        // add the final state of the benchmark
        TaskMachine.append(new Task('finish', TaskMachine,
            function() {
                // if the app is still listening, send a 'done' message
                AppComm.sendStateInformation('done');

                // close this tab, if running from the APP
                if (VellamoConsts.browserImageName !== null) {
                    if (VellamoConsts.benchmarkEndIndex !== VellamoConsts.BenchmarkDescriptions.length) {
                        // ...unless we're just switching intents because we're re-starting mongoose, so we're not actually "done"
                        return;
                    }

                    // remove the current iframe (disabled for removing everything)
                    //SurfaceLayouter.resetContainer(SurfaceLayouter.iFrameElement);

                    // try to close whole tab (not supported in all browsers)
                    // we're not using the much more reliable "open(location, '_self').close();",
                    // because when it doesn't work it reloads the page, looping
                    window.close();

                    // show a completion message right away
                    $('body').html(
                        "<div id='vs_thankyou_container'>" +
                        " <div class='vs-thankyou'>" +
                        "  <div class='vs-thankyou-title'>" +
                        "    Done!" +
                        "  </div>" +
                        " </div>" +
                        "</div>"
                    );

                    // don't leave the last benchmark run sitting in the browser
                    setTimeout(function() {
                        $('body').css('display', 'none');
                        $('body').html(
                            "<div id='vs_thankyou_container'>" +
                            " <div class='vs-thankyou'>" +
                            "  <div class='vs-thankyou-title'>" +
                            "    Vellamo was here!" +
                            "  </div>" +
                            "  <div class='vs-thankyou-content'>" +
                            "    Thank you for running Vellamo on this Browser.<br>" +
                            "    You can <a href='javascript:window.open(\"\",\"_self\").close();' style='text-decoration: underline; color: #888'>close this tab</a> now.<br>" +
                            "    <br>" +
                            "    <div style='color:#0087b7'>" +
                            "      Your results will be available in the <a href='vellamo://back-from-browser' style='text-decoration: underline; color: #0087b7;'>Vellamo APP</a>." +
                            "    </div>" +
                            "  </div>" +
                            " </div>" +
                            "</div>"
                        );
                        $('body').fadeIn(1000);
                    }, 2000);

                    // we intentionally never terminate this task. we want to block here
                    ///this.taskDone();

                    // adios
                    return;
                } else {
                    // show stats, if running from the Web/Desktop Browser
                    var message = 'You can close<br>this tab now.';

                    // show all the results for the web version
                    if (true) {
                        VellamoConsts['BenchmarkLookup'] = {};
                        for (var i = 0; i < VellamoConsts.BenchmarkDescriptions.length; i++) {
                            var description = VellamoConsts.BenchmarkDescriptions[i];
                            VellamoConsts.BenchmarkLookup[description.benchmarkId] = description;
                        }
                        $('#vs_topbar_info_name').html('<!-- span style="color:red;">.</span -->Results');
                        var rawResults = {};
                        var scores = {};
                        var totalScore = 0;
                        var uniq = 1;
                        State.benchmarks.forEach(function (benchmark) {
                            var benchmarkId = benchmark.benchmarkId.replace('vellamo.browser.','');
                            benchmark.output.computeScore();
                            rawResults[benchmarkId+(uniq++)] = benchmark.output;
                            scores[benchmarkId] = Math.round(benchmark.output.score);
                            totalScore += benchmark.output.score;
                        });
                        var scoresString = JSON.stringify({ total: Math.round(totalScore), benchmarks: scores }, null, '  ');
                        var detailsString = JSON.stringify(rawResults, null, '  ');
                        message += '<pre style="text-align: left; background: #EEE; padding: 10px;">';
                        message += 'Scores:\n';
                        message += scoresString.substring(1, scoresString.length-1);
                        message += '\nRaw Results:\n';
                        message += detailsString.substring(1, detailsString.length-1);
                        message += '</pre>';
                        $('html').css('overflow', 'visible');
                        $('body').css('overflow', 'visible');
                    }
                    // The following will disrupt a little bit more:
                    //$('body').html(message)
                    SurfaceLayouter.setContentInlineMessage(message);
                    SurfaceLayouter.setContentBackgroundColor('#F3F3F3');

                    // in desktop mode there may be something else to be done
                    this.taskDone();
                }
            }
        ));

        // add the quick benchmark buttons to switch fast
        if (VellamoConsts.debug > 0) {
            $('#vs_actions').append('<div onclick="document.location = \'?\'+Math.floor((1 + Math.random()) * 0x10000).toString(16).substring(1);">Refresh</div>');
            for (var i = 0; i < State.benchmarks.length; ++i)
                $('#vs_actions').append('<div onclick="VellamoShell.debugStartBenchmark('+i+')">'+i+'</div>');
        }

        // Ready, Set, Go!
        TaskMachine.resume();
    }

    function debugStartBenchmark(n) {
        State.reset();
        TaskMachine.emptyLeaveRunning();
        SurfaceLayouter.resetContent();
        TaskMachine.append(TaskMachine.make_T_Preloader(State.benchmarks[n]));
        TaskMachine.append(TaskMachine.make_T_Benchmark(State.benchmarks[n]));
    }

    window.VellamoShell = {
        onDocumentReady : onDocumentReady,
        onSurfaceChanged : SurfaceLayouter.onSurfaceChanged,
        registerBenchmarkMessages : BenchmarkMessageHub.register,
        debugStartBenchmark : debugStartBenchmark,
        Debugger : $SD,
        abort : AppComm.shellAbort
    };

})(this);

if (VellamoConsts.browserImageName) {
	$('#vs_topbar_title').text("");	//partly covered and quite redundant when run from app
} else {
	$('#vs_topbar_title').html(VellamoConsts.name + "<br/>" + VellamoConsts.version);
}
if (VellamoConsts.warnUserAboutSession) {
    var warning = document.createElement("div");
    warning.innerHTML ='<b>Restarted</b>&nbsp;<button type="button" onclick="VellamoShell.abort();">Quit?</button>';
    warning.style.color = "darkred";
    document.getElementById("vs_topbar_title").appendChild(warning);
    var cur = window.getComputedStyle(warning, null).fontSize;
    var size = parseInt(cur.replace(/\D+/g,''),10);
    var unit = cur.replace(/\d+/g,'');
    warning.style.fontSize = size / 2 + unit;
}
$(document).ready(VellamoShell.onDocumentReady);
$(window).bind('orientationchange resize', VellamoShell.onSurfaceChanged);
VellamoShell.registerBenchmarkMessages();
