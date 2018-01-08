"use strict";

let display, user;
let curIndex, pattern;
let score, result;

const COLOR_MAP = {
	0: "blue",
	1: "red",
	2: "green",
	3: "yellow"
};

function start() {
	let startButton = document.createElement("div");
	startButton.classList.add("button");
	startButton.id = "start";
	startButton.innerHTML = "Start Simon";
	startButton.addEventListener("click", init);
	
	let temp = document.createElement("br");
	temp.id = "temp";
	
	let gameDiv = document.getElementById("game_window");
	gameDiv.appendChild(temp);
	gameDiv.appendChild(startButton);
}

function init() {
	display = document.getElementsByClassName("display");
	user = document.getElementsByClassName("user");
	
	curIndex = score = result = 0;
	pattern = [];
	
	let gameDiv = document.getElementById("game_window");
	let startButton = document.getElementById("start");
	if (startButton !== null) {
		gameDiv.removeChild(startButton);
	}
	
	let br = document.getElementById("temp");
	if (br !== null) {
		gameDiv.removeChild(br);
	}
	
	simon_exec().then(() => {
		user_run();
	});
}

function restart() {
	for (let x = 0; x < 4; x++) {
		user[x].style = "";
		display[x].style = "";
	}
	
	//both restartButton and finalScore should exist together
	let restartButton = document.getElementById("restart");
	let finalScore = document.getElementById("finalScore");
	
	let gameDiv = document.getElementById("game_window");
	
	gameDiv.removeChild(finalScore);
	gameDiv.removeChild(restartButton);
	
	init();
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
			
			setTimeout(() => {
				display[index].classList.remove(COLOR_MAP[index]);
				display[index].classList.add("disabled");
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
		endGame();
		return;
	}
	
	pattern.push(Math.floor(Math.random() * 4));
	console.log("pattern: " + pattern);
	
	await display_run(pattern);
	console.log("display_run finished");
	
	return;
}

function sendScore(username, score) {
	//get username in here?
	
	$.ajax({
		url: "<some path>",
		method: "POST",
		data: {
			username,
			score
		}
	});
}

window.onload = start;

