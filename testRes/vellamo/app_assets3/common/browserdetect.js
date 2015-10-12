//Detect various browser and system details

function SysInfo() {
}

var screenInfo = [];
var browserInfo =[];
var UNKNOWN = -1;

//Detect Screen details
if (screen.width) {
  screenInfo.width = (screen.width) ? screen.width : UNKNOWN;
  screenInfo.height = (screen.height) ? screen.height : UNKNOWN;
}

browserInfo.browser = navigator.appName;
browserInfo.ua = navigator.userAgent;
browserInfo.version = navigator.appVersion;

SysInfo.getSysInfo = function() {
  return (SysInfo.getScreenInfo() + SysInfo.getBrowserInfo() +
          SysInfo.getUAInfo() + SysInfo.getVersionInfo());
  /*
   * return ("Screen Width: " + screenInfo.width + " Screen Height: " + screenInfo.height +
   *   " Browser: " + browserInfo.browser + " UA: " + browserInfo.ua + " Browser Version: " + browserInfo.version);
   */
}

SysInfo.getScreenInfo = function() {
  return ("Screen Width: " + screenInfo.width + " Height: " + screenInfo.height + " ");
}

SysInfo.getBrowserInfo = function() {
  return ("Browser: " + browserInfo.browser + " ");
}

SysInfo.getUAInfo = function() {
  return ("UA: " + browserInfo.ua + " ");
}

SysInfo.getVersionInfo = function() {
  return ("Version: " + browserInfo.version + " ");
}

