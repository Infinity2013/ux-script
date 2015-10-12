importScripts('lib/mjs.js');
var jellyfishTargets = {};
jellyfishTargets.objName = "targets";
jellyfishTargets.count = 0;
jellyfishTargets.order = [];
jellyfishTargets.order3D = [];

JellyfishTarget = function(tx,ty,tz,scl,id,time){
  this.pos = V3.$(tx,ty,tz);
  this.scl = scl;
  this.id = id;
  this.time = Math.random()*100;
  this.speed = Math.random()+0.5;
  this.alive = 1;
};

var delta;
var dist;
var dir;
var force;
var s1,s2;

//!!!
var magnitude, magSum = 0, magCount = 0, magAverage = 0.1111111111111111111;
//!!!

function Param(){
  //jellyfish
  this.jCount = 5;
  this.jScale = 4;
  this.jScaleRandom = 0;
  this.jTurb = 0.05;
  this.jSpeed = 0.01;
  this.pBbox = [80,80,80];
}

var testParam = new Param();

function simulate(){
  var serverTime = new Date();
  var serverMilis = serverTime.getTime()%100000000/1000;
  serverTime.hours = (serverTime.getHours()+6)%24;
  serverTime.minutes = serverTime.getMinutes();
  serverTime.seconds = serverTime.getSeconds();
  serverTime.total = serverTime.hours*3600 + serverTime.minutes*60 + serverTime.seconds;

  var i = 0;
  if(jellyfishTargets.count<testParam.jCount){
    jellyfishTargets[jellyfishTargets.count] = new JellyfishTarget(
            Math.random(i)*2*testParam.pBbox[0]-testParam.pBbox[0],
            Math.random(i)*2*testParam.pBbox[1]-testParam.pBbox[1]-40,
            Math.random(i)*2*testParam.pBbox[2]-testParam.pBbox[2],
            Math.random(i)*testParam.jScaleRandom+testParam.jScale,
            jellyfishTargets.count,
            serverMilis
    );
    jellyfishTargets.order.push([jellyfishTargets.count,0]);
    jellyfishTargets.order3D.push([jellyfishTargets.count,0]);
    jellyfishTargets.count += 1;
    i++;
  }
  else if(jellyfishTargets.count>testParam.jCount){
    jellyfishTargets.order3D.pop();
    jellyfishTargets.order.pop();
    jellyfishTargets.count -= 1;
    delete jellyfishTargets[jellyfishTargets.count];
  }

  for(var i=0; i < jellyfishTargets.count; i++){

    //SET TIME
    jellyfishTargets[i].time += (testParam.jSpeed*16/(jellyfishTargets[i].scl+1))*jellyfishTargets[i].speed;

    //MOVE
    var time = new Date().getTime();
    var speed = jellyfishTargets[i].scl*testParam.jSpeed*2.8;
    var flow = V3.$(
            speed*Math.sin((jellyfishTargets[i].pos[2]+jellyfishTargets[i].id+time/10000)*testParam.jTurb),
            speed*Math.sin((jellyfishTargets[i].pos[0]+jellyfishTargets[i].id+time/10000)*testParam.jTurb),
            speed*Math.sin((jellyfishTargets[i].pos[1]+jellyfishTargets[i].id+time/10000)*testParam.jTurb)
    );

    V3.add(jellyfishTargets[i].pos, flow, jellyfishTargets[i].pos);

    //REPEL
    for(var j=0; j < jellyfishTargets.count; j++){
      if (i != j){
        s1 = jellyfishTargets[i].scl*4;
        s2 = jellyfishTargets[j].scl*4;
        delta = V3.sub(jellyfishTargets[i].pos, jellyfishTargets[j].pos);
        dist = V3.length(delta);// - (jellyfishTargets[i].scl+jellyfishTargets[j].scl)*6;
        dir = V3.normalize(delta);
        //if (dist < 12+s1+s2){

        //force = V3.scale(dir,Math.pow(Math.max(0,(4-dist+s1+s2)),3)*0.25);

//!!!
        var magnitude = Math.pow(1/dist, 3)*20000;
        if (magnitude > 10 * magAverage) {
//        	console.log("magnitude="+magnitude+", magAverage="+magAverage);
          magnitude = 10 * magAverage;
        }
        magSum += magnitude;
        magCount += 1;
        magAverage = magSum / magCount;
//!!!

        force = V3.scale(dir, magnitude);


        V3.add(jellyfishTargets[i].pos, force, jellyfishTargets[i].pos);
        //}
      }
    }

    //CENTER
    jellyfishTargets[i].pos[0] *= 0.995;
    jellyfishTargets[i].pos[1] *= 0.995;
    jellyfishTargets[i].pos[2] *= 0.995;

  }
}

self.addEventListener('message', function(e) {
  if (e == null) {
    self.postMessage({'status': 'FAILED'});
    return;
  }
  var data = e.data;
  if (data == null) {
    self.postMessage({'status' : 'FAILED'});
    return;
  }
  switch (data.cmd) {
    case 'start':
      self.postMessage({'status' : 'STARTED'});
      break;
    case 'updateParams':
      testParam.jCount = data.count;
      simulate();
      var jsonText = JSON.stringify(jellyfishTargets);
      self.postMessage({'status' : 'SUCCESS', 'physics' : jsonText});
      break;
    case 'stop':
      self.postMessage({'status' : 'STOPPED'});
      self.close();
      break;
    default:
      self.postMessage({'status' : 'FAILED'});
  };
}, false);


