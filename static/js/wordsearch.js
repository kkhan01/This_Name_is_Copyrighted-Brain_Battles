"use strict";

let wordlist, grid;
let wordsAdded;
let wordTable, wordBank;

let answers = [
	/*
	format:
	
	{
		word: <string>
		row: <num>,
		col: <num>,
		reverse: <false or true>,
		direction: [
			<deltaRow>, <deltaCol>
		]
	},
	...
	*/
];
let wordsFound, startTime;

/*
plan for validation:
limit user to one word selection at a time
maintain another array of correct selections (aethetic thing)

check from top left:
	should never encounter the middle of a selection first
if selected cell encountered:
	look in all eight directions
	if a selected cell is found:
		find appropiate direction
		recursive:
			go to next cell based on direction
			if no more cell in the direction:
				validate all letters encountered up to the point

important notes:
	will not check for invalid selections, will just use first valid subpattern
*/

const BLANK_CHAR = "-";
const GRID_LEN = 10;
const DIRECTIONS = {
	WEST: [0, -1],
	SOUTHWEST: [1, -1],
	SOUTH: [1, 0],
	SOUTHEAST: [1, 1],
	EAST: [0, 1],
	NORTHEAST: [-1, 1],
	NORTH: [-1, 0],
	NORTHWEST: [-1, -1]
};
Object.freeze(DIRECTIONS);
for (let d in DIRECTIONS) Object.freeze(DIRECTIONS[d]);	//effectively an enum now
const DIRECTIONS_LEN = 8;

function constructList(s, num, min, max) {
    let temp = s.split(" ");
    //console.log(list);
    for (let i in temp){
	//console.log(list[i]);
	if(wordlist.length < num && temp[i].length <= max && temp[i].length >=min && wordlist.indexOf(temp[i]) == -1){
	    wordlist.push(temp[i]);
	}
    }
    console.log(wordlist);
}

//appends DOM elem to gameContainer
function appendMain(elem) {
	let gameDiv = document.getElementById("gameContainer");
	gameDiv.appendChild(elem);
}

//elem is a DOM object. removes the elem if it exists
function removeElem(elem) {
	let gameDiv = document.getElementById("gameContainer");
	if (elem !== null) {
		gameDiv.removeChild(elem);
	}
}

//create the html word table
function createTable() {
	wordTable = document.createElement("table");
	wordTable.id = "wordTable";
	let body = document.createElement("tbody");
	let row, data;
	
	for (let x of grid) {
		row = document.createElement("tr");
		
		for (let y of x) {
			data = document.createElement("td");
			data.classList.add("letter");
			data.classList.add("unselected");
			data.innerHTML = y;
			
			data.addEventListener("click", e => {
				let elem = e.target;
				
				if (elem.classList.contains("unselected")) {
					elem.classList.remove("unselected");
					elem.classList.add("selected");
				}
				else if (elem.classList.contains("selected")) {
					elem.classList.remove("selected");
					elem.classList.add("unselected");
				}
			});
			
			row.appendChild(data);
		}
		
		body.appendChild(row);
	}
	
	wordTable.appendChild(body);
	appendMain(wordTable);
}

//create the word bank
function createBank() {
	//for css
	let container = document.createElement("div");
	container.id = "wordBankContainer";
	
	wordBank = document.createElement("ul");
	wordBank.id = "wordBank";
	let item;
	
	for (let word of answers) {
		item = document.createElement("li");
		item.className = "word";
		
		if (word["reverse"]) {
			item.innerHTML = reverse(word["word"]);
		}
		else {
			item.innerHTML = word["word"];
		}
		
		wordBank.appendChild(item);
	}
	
	container.appendChild(wordBank);
	appendMain(container);
}

function getWordTableElem(row, col) {
	return wordTable.children.item(0).children.item(row).children.item(col);
}

//based on GRID_LEN
function outOfRange(row, col) {
	let r = row;
	let c = col;
	
	return r < 0 || r >= GRID_LEN || c < 0 || c >= GRID_LEN;
}

function obtainSelection() {
	//holds all selected cells
	/*
	for each elem:
	
	{
		elem: <DOM element>,
		row: <num>,
		col: <num>
	}
	*/
	let selected;
	let elem;
	let body = wordTable.children.item(0);	//everything is in a <tbody>
	
	for (let row = 0; row < body.children.length; row++) {
	for (let col = 0; col < body.children.item(row).children.length; col++) {
		selected = [];
		elem = getWordTableElem(row, col);
		if (elem.classList.contains("selected")) {
			selected.push({
				elem,
				row,
				col
			});
			
			//search for surrounding selected squares
			let tRow, tCol;
			for (let key of Object.keys(DIRECTIONS)) {
				let delta = DIRECTIONS[key];
				tRow = row + delta[0];
				tCol = col + delta[1];
				if (outOfRange(tRow, tCol) || !getWordTableElem(tRow, tCol).classList.contains("selected")) continue;
				
				//now keep going until out of range or no more selected squares
				let temp;
				while ( !outOfRange(tRow, tCol) && getWordTableElem(tRow, tCol).classList.contains("selected") ) {
					temp = getWordTableElem(tRow, tCol);
					selected.push({
						elem: temp,
						row: tRow,
						col: tCol
					});
					
					tRow += delta[0];
					tCol += delta[1];
				}
				
				return selected;
			}
		}
	}
	}
	
	return null;
}

function checkSelection() {
	let selection = obtainSelection();
	if (selection === null) return;
	
	let letters = [];
	for (let s of selection) {
		letters.push(s.elem.innerHTML);
	}
	let word = letters.join("");
	
	let current;
	//either start at the beginning of selection or end of selection
	for (let x = 0; x < 2; x++) {
		current = (x == 0) ? selection[0] : selection[selection.length-1];
		for (let elem of answers) {
			if (current.row == elem.row && current.col == elem.col) {
				if (word === elem.word ||
						word === reverse(elem.word)) {
					console.log("match found");
					
					//set all the letters to a special "found" class
					for (let s of selection) {
						s.elem.classList.remove("selected");
						s.elem.classList.add("unselected");
						s.elem.classList.add("found");
					}
					
					//highlight word in word bank (mark as found)
					for (let w of wordBank.children) {
						if (w.innerHTML === word || w.innerHTML === reverse(word)) {
							w.classList.add("found");
							break;
						}
					}
					
					if (++wordsFound >= answers.length) {
						console.log("all words found");
						endGame();
					}
					
					return;
				}
			}
		}
	}
	console.log("no match");
	//set all the letters back to unselected
	for (let s of selection) {
		s.elem.classList.remove("selected");
		s.elem.classList.add("unselected");
	}
}

function sendScore(score) {
	ajaxP({
		url: '/addscore',
		data : { game : 'search', score : ''+score },
		type: 'POST'
	});
}

function endGame() {
	let totalTime = (Date.now() - startTime) / 1000;
	
	let total = document.createElement("h3");
	total.id = "totalTime";
	total.innerHTML = Math.round(totalTime) + " seconds total";
	appendMain(total);
	console.log("time elapsed: " + totalTime);
	
	let avgTime = document.createElement("h3");
	avgTime.id = "avgTime";
	avgTime.innerHTML = Math.round(totalTime / answers.length) + " seconds per word";
	appendMain(avgTime);
	console.log("time per word: " + (totalTime / answers.length));
	
	sendScore(Math.round(totalTime / answers.length));
	
	let restartButton = document.createElement("div");
	restartButton.classList.add("button");
	restartButton.id = "restart";
	restartButton.innerHTML = "Play Again";
	restartButton.addEventListener("click", restart);
	appendMain(restartButton);
}

function reset() {
	wordlist = [];
	grid = [];
	wordsAdded = [];
	wordsFound = 0;
	answers = [];
	wordTable = null;
	wordBank = null;
	
	for (let y = 0; y < GRID_LEN; y++) {
		grid.push([]);
		for (let x = 0; x < GRID_LEN; x++) {
			grid[y].push(BLANK_CHAR);
		}
		
	}
}

function init() {
	reset();
	
	let introText = document.createElement("p");
	introText.id = "introText";
	introText.innerHTML = `Instructions:
Click a letter to select it.
Click the "Check" button to check your selection.
Only check one word at a time.
`;
	appendMain(introText);
	
	let startButton = document.createElement("div");
	startButton.id = "startButton";
	startButton.classList.add("button");
	startButton.innerHTML = "Start";
	startButton.addEventListener("click", start);
	
	appendMain(startButton);
}

function restart() {
	removeElem(wordTable);
	
	let elem = document.getElementById("validate");
	removeElem(elem);
	
	elem = document.getElementById("wordBankContainer");
	removeElem(elem);
	
	elem = document.getElementById("totalTime");
	removeElem(elem);
	
	elem = document.getElementById("avgTime");
	removeElem(elem);
	
	elem = document.getElementById("restart");
	removeElem(elem);
	
	reset();
	
	start();
}

//ajax with promise
function ajaxP(settings) {
	return new Promise((resolve, reject) => {
		$.ajax(settings).done(resolve).fail(reject);
	});
}

function start() {
	ajaxP({
		url: 'http://www.randomtext.me/api/gibberish/p-1/100',
		type: 'GET'
	})
	.then( data => {			//we don't plan on using the status
		console.log("constructing word list");
		let randomwords = data["text_out"].replace("<p>","").replace("</p>","").toUpperCase();
		constructList(randomwords,10,4,8);
	})
	.then(() => {
		console.log("filling word grid");
		addWords();
		fillRandom();
	})
	.then(() => {
		console.log("printing answers");
		console.log(answers);
	})
	.then(() => {
		console.log("printing grid");
		printGrid(grid);
	})
	.then(() => {			//remove please wait
		console.log("removing wait notification");
		let waitMsg = document.getElementById("wait");
		removeElem(waitMsg);
	})
	.then(() => {			//construct html table
		console.log("generating html table");
		createTable();
	})
	.then(() => {
		console.log("creating word bank");
		createBank();
	})
	.then(() => {
		console.log("adding validation button");
		let validate = document.createElement("div");
		validate.id = "validate";
		validate.className = "button";
		validate.innerHTML = "Check";
		validate.addEventListener("click", e => {
			checkSelection();
		});
		appendMain(validate);
	})
	.then(() => {
		console.log("starting timer");
		startTime = Date.now();
	});
	
	let startButton = document.getElementById("startButton");
	removeElem(startButton);
	
	let introText = document.getElementById("introText");
	removeElem(introText);
	
	//add a "please wait notification"
	let waitMsg = document.createElement("h4");
	waitMsg.innerHTML = "Please wait";
	waitMsg.id = "wait";
	appendMain(waitMsg);
}

function reverse(s) {
	return s.split("").reverse().join("");
}

function printGrid(grid) {
	let temp;
	for (let x of grid) {
		temp = "";
		for (let y of x) {
			temp += y + " ";
		}
		console.log(temp);
	}
}

function fillRandom() {
	let lo = "A".charCodeAt(0);
	let hi = "Z".charCodeAt(0)+1;
	
	for (let x = 0; x < GRID_LEN; x++) {
		for (let y = 0; y < GRID_LEN; y++) {
			if (grid[x][y] == BLANK_CHAR) {
				grid[x][y] = String.fromCharCode( Math.floor(Math.random() * (hi-lo) + lo));
			}
		}
	}
}

function addWords() {
	let row, col;
	for (let word of wordlist) {
		row = Math.floor(Math.random() * DIRECTIONS_LEN);
		col = Math.floor(Math.random() * DIRECTIONS_LEN);
		
		addSingleWord(word, row, col);
	}
	
	printGrid(grid);
}

function addSingleWord(word, row, col){
	let counter;
	let tRow, tCol;
	let delta;
	
	for (let turn = 0; turn < 2; word = reverse(word), turn++) {	//forward and reverse
		for (let x = 0; x < 3; x++) {
			//random direction
			delta = DIRECTIONS[ Object.keys(DIRECTIONS)[ Math.floor(Math.random() * DIRECTIONS_LEN)] ];
			tRow = row;
			tCol = col;
			
			
			//first, check if we can place it
			for (counter = 0; counter < word.length; counter++) {
				//if out of bounds
				if (tRow < 0 || tRow >= grid.length || tCol < 0 || tCol >= grid[0].length) break;
				
				//if word can't overlap
				if (grid[tRow][tCol] !== BLANK_CHAR && grid[tRow][tCol] !== word[counter]) break;
				
				tRow += delta[0];
				tCol += delta[1];
			}
			
			//try a new direction
			if (counter != word.length) break;
			tRow = row;
			tCol = col;
			
			//now actually place it
			for (counter = 0; counter < word.length; counter++) {
				grid[tRow][tCol] = word[counter];
					
				tRow += delta[0];
				tCol += delta[1];
			}
			
			//add to answer key
			answers.push({
				word,
				row,
				col,
				reverse: turn == 1,
				direction: delta
			});
			
			wordsAdded.push(word);
			return true;
		}
	}
	
	return false;
}


init();
//start();

