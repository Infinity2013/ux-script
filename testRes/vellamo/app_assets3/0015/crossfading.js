/*
  This file is part of the Ofi Labs X2 project.

  Copyright (C) 2011 Ariya Hidayat <ariya.hidayat@gmail.com>

  Redistribution and use in source and binary forms, with or without
  modification, are permitted provided that the following conditions are met:

	* Redistributions of source code must retain the above copyright
	  notice, this list of conditions and the following disclaimer.
	* Redistributions in binary form must reproduce the above copyright
	  notice, this list of conditions and the following disclaimer in the
	  documentation and/or other materials provided with the distribution.
	* Neither the name of the <organization> nor the
	  names of its contributors may be used to endorse or promote products
	  derived from this software without specific prior written permission.

  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
  ARE DISCLAIMED. IN NO EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY
  DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
  (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
  LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF
  THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/

/*global window:true Int16Array:true */

function Crossfader(canvas, image1, image2, console) {

	var context = canvas.getContext('2d'),
        width = canvas.width,
        height = canvas.height,
        len = 4 * width * height,
        loadScale = len/(512*512*4),
		source,
		target,
		result,
		frames = 0,
		value = 0,
        cumulativeTime = 0,
		disposing = false;

	function init() {
        if (width !== 512 || height !== 512)
			console.warn('Canvas issue: width ('+width+') and height ('+height+') are not expected, check this.');

		canvas.style.opacity = 1;

		context.fillStyle = "rgb(0,0,0)";
		context.fillRect(0, 0, width, height);

		context.drawImage(image1, 0, 0);
		source = context.getImageData(0, 0, width, height);

		context.fillStyle = "rgb(0,0,0)";
		context.fillRect(0, 0, width, height);

		context.drawImage(image2, 0, 0);
		target = context.getImageData(0, 0, width, height);

		result = context.createImageData(width, height);

        context.fillStyle = '#f80';
        //context.fillRect(0, 0, width, height);
        context.drawImage(image1, 0, 0);
    }

	function tween(factor) {
		var i, s, t, r;
		s = source.data;
		t = target.data;
		r = result.data;
		for (i = 0; i < len; i += 4) {
			r[i] = t[i] + (s[i] - t[i]) * factor;
			r[i + 1] = t[i + 1] + (s[i + 1] - t[i + 1]) * factor;
			r[i + 2] = t[i + 2] + (s[i + 2] - t[i + 2]) * factor;
			r[i + 3] = 255;
		}
	}

    function unitOfWork() {
        if (disposing === true)
            return;
        value += 0.1;
        var factor = 0.5 + 0.5 * Math.sin(value);
        var startTime = Date.now();
        tween(factor); // first pass
        tween(factor); // second pass
        cumulativeTime += (Date.now() - startTime);
        frames += 1;
        context.putImageData(result, 0, 0);
    }

	function dispose() {
		disposing = true;
	}

    function crossfadeRate() {
        return cumulativeTime ? (1000 * frames / cumulativeTime) : 0;
	}

	init();

	return {
		loop: unitOfWork,
		dispose: dispose,
        crossfadeRate: crossfadeRate,
        loadScale: loadScale
	};
}
