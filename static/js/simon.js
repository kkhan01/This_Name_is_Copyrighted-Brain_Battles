"use strict";

let display, user;
let curIndex, pattern;
let score, result;

let soundArray;

const COLOR_MAP = {
	0: "blue",
	1: "red",
	2: "green",
	3: "yellow"
};

//this is actually in terms of project root, not sure why
const SOUND_DIR = "static/media/";

const SOUND_FILES = [
	"piano-a.wav",
	"piano-b.wav",
	"piano-c.wav",
	"piano-d.wav"
];

//elem is a DOM object. removes the elem if it exists
function removeElem(elem) {
	let gameDiv = document.getElementById("game_window");
	if (elem !== null) {
		gameDiv.removeChild(elem);
	}
}

function initSounds() {
	let res = [];
	
	for (let x = 0; x < SOUND_FILES.length; x++) {
		res.push( document.createElement("audio") );
		res[x].src = SOUND_DIR + SOUND_FILES[x];
	}
	
	return res;
}

function start() {
	display = document.getElementsByClassName("display");
	user = document.getElementsByClassName("user");
	
	//curIndex = score = result = 0;
	//pattern = [];
	
	soundArray = initSounds();

	let startButton = document.createElement("div");
	startButton.classList.add("button");
	startButton.id = "start";
	startButton.innerHTML = "Start Simon";
	startButton.addEventListener("click", restart);
	
	let temp = document.createElement("br");
	temp.id = "temp";
	
	let gameDiv = document.getElementById("game_window");
	gameDiv.appendChild(temp);
	gameDiv.appendChild(startButton);
}

function restart() {
	for (let x = 0; x < 4; x++) {
		user[x].style = "";
		display[x].style = "";
	}
	
	curIndex = score = result = 0;
	pattern = [];
	
	//list of elem ids to remove
	let targetElems = [
		"restart",
		"finalScore",
		"start",
		"temp",
		"restart"
	];
	
	for (let elem of targetElems) {
		removeElem( document.getElementById(elem) );
	}
	
	simon_exec().then(() => {
		user_run();
	});
	
}

//doesn't actually set to black, cuz the disabled CSS class does some stuff
//it's actually gray (which isn't a bad color)
function endGame() {
	userClear();
	for (let x = 0; x < 4; x++) {
		user[x].style.backgroundColor = "black";
		display[x].style.backgroundColor = "black";
	}
	
	let scoreElem = document.createElement("h3");
	scoreElem.id = "finalScore";
	scoreElem.innerHTML = "Final score: " + score;
	
	let temp = document.createElement("br");
	temp.id = "temp";
	
	let restartButton = document.createElement("div");
	restartButton.classList.add("button");
	restartButton.id = "restart";
	restartButton.addEventListener("click", restart);
	restartButton.innerHTML = "Play Again";
	
	let gameDiv = document.getElementById("game_window");
	gameDiv.appendChild(scoreElem);
	gameDiv.appendChild(temp);
	gameDiv.appendChild(restartButton);
	
	//call sendScore
}

//For some reason, this doesn't work inside of a promise
//I don't why
function userClear() {
	for (let x = 0; x < 4; x++) {
		//disable button
		user[x].classList.remove(COLOR_MAP[parseInt(user[x].id)]);
		user[x].classList.add("disabled");
		
		user[x].removeEventListener("click", correctClick);
	}
}

//Every button press will call this
function correctClick() {
	let index = parseInt(this.id);
	if (index != pattern[curIndex++]) {
		console.log("oh no");
		
		//simon_exec will end the game if result is -1
		result = -1;
		simon_exec();
	}
	else if (curIndex >= pattern.length) {
		console.log("we did it");
		score++;
		userClear();
		simon_exec().then(() => {
			user_run();
		});
	}
}

//Make user buttons available to use
function user_run() {
	curIndex = 0;
	
	for (let x = 0; x < 4; x++) {
		//enbale button
		user[x].classList.remove("disabled");
		user[x].classList.add(COLOR_MAP[parseInt(user[x].id)]);
		
		user[x].addEventListener("click", correctClick);
	}
}

//pattern should be a list of numbers 0-3 specifying which buttons to light up
function display_run(pattern) {
	let exec = Promise.resolve();
	for (let index of pattern) {
		//sequentially run through all the display buttons
		exec = exec.then(() => {
		return new Promise(resolve => {
		setTimeout(() => {
			//change button color by adding it to another CSS class
			display[index].classList.remove("disabled");
			display[index].classList.add(COLOR_MAP[index]);
			//play sound
			soundArray[index].play();
			
			setTimeout(() => {
				display[index].classList.remove(COLOR_MAP[index]);
				display[index].classList.add("disabled");
				//stop sound, reset timer on it
				soundArray[index].pause();
				soundArray[index].currentTime = 0;
				
				resolve(index);
			}, 500);	//change this interval to change flashing speed
			
		}, 1000);		//change this interval to change wait time between button flashes
		});
		});
	}
	
	return exec;
}

//main reason this is async is so program will "block" on display_run
//also legacy reasons
async function simon_exec() {
    if (result == -1) {
	console.log("final score: " + score);
	sendScore(score);
	endGame();
	return;
    }
    
    pattern.push(Math.floor(Math.random() * 4));
    console.log("pattern: " + pattern);
    
    await display_run(pattern);
    console.log("display_run finished");
    
    return;
}

function sendScore(uscore) {
	$.ajax({
	    url: '/addscore',
	    data : { game : 'simon', score : ''+uscore },
	    type: 'POST',
	    success: function(d) {
		console.log(d);
	    } //end success callback
	});//end ajax call
}

window.onload = start;

