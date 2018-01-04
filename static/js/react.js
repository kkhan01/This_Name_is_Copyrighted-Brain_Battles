var box = document.getElementById("gamebox");
var body = document.getElementsByTagName("body")[0];
var start = document.getElementById("start");
var boxHeight = box.offsetHeight;
var boxWidth = box.offsetWidth;
box.setAttribute("style","background-color:#0099CC;");
var directions = document.createElement("h1");
directions.setAttribute("style","position:relative;top:50%");
directions.innerHTML = "Click anywhere to start!";
box.appendChild(directions);
var activate = 0;
var randTime = 2000 + Math.floor(Math.random()*8000);
var needclick = 2;
var timeoutevent;


var startup = function(){
    box.setAttribute("style","background-color:#ff3f3f;");
    directions.innerHTML = "Wait for it...";
    needclick = 0;
    timeoutevent = setTimeout(go,randTime);
};

var go = function(){
    box.setAttribute("style","background-color:#43f961;");
    directions.innerHTML = "Click!";
    needclick = 1;
    var date = new Date();
    activate = date.getTime();
};

var onClick = function(e){
    if(needclick == 1){
	var newdate = new Date();
	var clicktime = newdate.getTime();
	this.setAttribute("style","background-color:#0099CC;");
	var reacttime = (clicktime - activate);
	directions.innerHTML = "" + reacttime + " ms";
	needclick = 2;
    }
    
    else if(needclick == 0){
	this.setAttribute("style","background-color:#0099CC;");
	directions.innerHTML = "Too soon, try again!";
	clearTimeout(timeoutevent);
	needclick = 2;
    }
    else{
	startup();
    }
    
};

console.log(start);
box.addEventListener("click", onClick);
