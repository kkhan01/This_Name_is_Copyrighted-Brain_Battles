var box = document.getElementById("box");
var body = document.getElementsByTagName("body")[0];
var start = document.getElementById("start");
var boxHeight = box.offsetHeight;
var boxWidth = box.offsetWidth;
var directions = document.createElement("h1");
var date = new Date();
var time = date.getTime();
var randTime = 2000 + Math.floor(Math.random()*8000);


var startup = function(e){
    this.remove();
    directions.innerHTML = "Wait for it...";
    box.appendChild(directions);
    box.setAttribute("style","background-color:red;");
    setTimeout(go,randTime);
};

var go = function(e){
    box.setAttribute("style","background-color:green;");
    directions.innerHTML = "Click!";
}


console.log(start);
start.addEventListener("click", startup);
