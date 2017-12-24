//code for simon

let display, user;

function init() {
	display = document.getElementsByClassName("display");
	user = document.getElementsByClassName("user");
	
}

//pattern should be a list of numbers 0-3 specifying which buttons to light up
function display_run(pattern) {
	let exec = Promise.resolve();
	for (let index of pattern) {
		exec = exec.then(() => {
			return new Promise(resolve => {
				setTimeout(() =>{
					console.log("wee" + index);
					resolve(index);
				}, 1000);
			});
		});
	}
}

init();
console.log(display);

display_run([0, 1, 2, 3]);


