let display, user;
let curIndex, pattern;
let score, result;

const COLOR_MAP = {
	0: "blue",
	1: "red",
	2: "green",
	3: "yellow"
};

function init() {
	display = document.getElementsByClassName("display");
	user = document.getElementsByClassName("user");
	
	curIndex = score = result = 0;
	pattern = [];
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
	scoreElem.innerHTML = "Final score: " + score;
	
	let gameDiv = document.getElementById("game_window");
	gameDiv.appendChild(scoreElem);
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
			}, 500);	//change this interval to change flashing speed
			
			resolve(index);
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
	
	user_run();
	return;
}

init();

simon_exec().then(() => {
	user_run();
});

