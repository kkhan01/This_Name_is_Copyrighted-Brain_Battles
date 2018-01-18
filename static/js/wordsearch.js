"use strict";

let wordlist, grid;
let wordsAdded;
let wordTable, wordBank;

let answers = {
	/*
	format:
	
	word: {
		row: <num>,
		col: <num>,
		reverse: <false or true>,
		direction: [
			<deltaRow>, <deltaCol>
		]
	},
	...
	*/
};

const BLANK_CHAR = "-";
const GRID_LEN = 10;
const DIRECTIONS = {
	NORTH: [0, -1],
	NORTHEAST: [1, -1],
	EAST: [1, 0],
	SOUTHEAST: [1, 1],
	SOUTH: [0, 1],
	SOUTHWEST: [-1, 1],
	WEST: [-1, 0],
	NORTHWEST: [-1, -1]
};
Object.freeze(DIRECTIONS);
for (let d in DIRECTIONS) Object.freeze(DIRECTIONS[d]);	//effectively an enum now
const DIRECTIONS_LEN = 8;

function transmit() {
	$.ajax({
		url: 'http://www.randomtext.me/api/gibberish/p-1/100',
		type: 'GET',
		success: function(d) {
			let randomwords = d["text_out"].replace("<p>","").replace("</p>","").toUpperCase();
			//console.log(randomwords);
			constructList(randomwords,10,4,8);
			//addWords();
			//addSingleWord(wordlist[0], 0, 0);
			//fillRandom();
		} //end success callback
	});//end ajax call
}; //end transmit function

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
			data.className = "letter";
			data.innerHTML = y;
			
			data.addEventListener("click", e => {
				let elem = e.target;
				
				if (elem.classList.contains("letter")) {
					elem.classList.remove("letter");
					elem.classList.add("selected");
				}
				else if (elem.classList.contains("selected")) {
					elem.classList.remove("selected");
					elem.classList.add("letter");
				}
			});
			
			row.appendChild(data);
		}
		
		body.appendChild(row);
	}
	
	//let gameContainer = document.getElementById("gameContainer");
	wordTable.appendChild(body);
	appendMain(wordTable);
	//gameContainer.appendChild(wordTable);
}

//create the word bank
function createBank() {
	wordBank = document.createElement("ul");
	wordBank.id = "wordBank";
	let item;
	
	for (let word in Object.keys(answers)) {
		item = document.createElement("li");
		item.className = "word";
		
		if (answers[word]["reverse"]) {
			item.innerHTML = reverse(word);
		}
		else {
			item.innerHTML = word;
		}
		
		wordBank.appendChild(item);
	}
	
	
}

function init() {
	wordlist = [];
	grid = [];
	wordsAdded = [];
	
	for (let y = 0; y < GRID_LEN; y++) {
		grid.push([]);
		for (let x = 0; x < GRID_LEN; x++) {
			grid[y].push(BLANK_CHAR);
		}
		
	}
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
	
	//add a "please wait notification"
	let gameContainer = document.getElementById("gameContainer");
	
	let waitMsg = document.createElement("h4");
	waitMsg.innerHTML = "Please wait";
	waitMsg.id = "wait";
	gameContainer.appendChild(waitMsg);
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
			answers[word] = {
				row,
				col,
				reverse: turn == 1,
				direction: delta
			};
			
			wordsAdded.push(word);
			return true;
		}
	}
	
	return false;
}


init();
//addSingleWord();
//transmit();
start();
//document.getElementById("input").addEventListener('input', transmit);
