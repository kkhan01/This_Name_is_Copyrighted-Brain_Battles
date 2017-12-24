//code for simon

let display, user;

const COLOR_MAP = {
	0: "blue",
	1: "red",
	2: "green",
	3: "yellow"
};

function init() {
	display = document.getElementsByClassName("display");
	user = document.getElementsByClassName("user");
}

function user_run(pattern) {
	for (let x = 0; x < 4; x++) {
		user[x].classList.remove("disabled");
		user[x].classList.add(COLOR_MAP[x]);
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
	
	//move this outside?
	//setup user buttons
	exec = exec.then(() => {
		return new Promise(resolve => {
			user_run();
			resolve();
		});
	});
}

init();
console.log(display);

display_run([3, 0, 1, 2, 1]);


