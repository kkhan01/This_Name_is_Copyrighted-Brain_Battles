let display, user;
let curIndex, pattern;
let score, result;

let gameStatus = new Promise(() => {});

const COLOR_MAP = {
	0: "blue",
	1: "red",
	2: "green",
	3: "yellow"
};

function init() {
	display = document.getElementsByClassName("display");
	user = document.getElementsByClassName("user");
	
	score = result = 0;
	pattern = [];
}

//For some reason, this doesn't work inside of a promise
//I don't why
function userClear() {
	for (let x = 0; x < 4; x++) {
		user[x].classList.remove(COLOR_MAP[parseInt(user[x].id)]);
		user[x].classList.add("disabled");
		
		user[x].removeEventListener("click", correctClick);
	}
}

function correctClick() {
	let index = parseInt(this.id);
	if (index != pattern[curIndex++]) {
		console.log("oh no");
		//gameStatus = Promise.resolve();
		result = -1;
		//return Promise.resolve(-1);
		simon_exec();
	}
	else if (curIndex >= pattern.length) {
		console.log("we did it");
		//gameStatus = Promise.resolve();
		score++;
		userClear();
		simon_exec().then(() => {
			user_run();
		});
	}
	
	console.log(gameStatus);
}

function user_run() {
	curIndex = 0;
	
	for (let x = 0; x < 4; x++) {
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
			display[index].classList.remove("disabled");
			display[index].classList.add(COLOR_MAP[index]);
			setTimeout(() => {
				display[index].classList.remove(COLOR_MAP[index]);
				display[index].classList.add("disabled");
			}, 500);
			
			console.log("wee" + index);
			resolve(index);
		}, 1000);
		});
		});
	}
	
	return exec;
}

async function simon_exec() {
	if (result == -1) {
		console.log("final score: " + score);
		//call end routine
		return;
	}
	
	pattern.push(Math.floor(Math.random() * 4));
	//pattern = [3, 0];
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

//display_run([3, 0, 1, 2, 1]);

