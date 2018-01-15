"use strict";

let wordlist, grid;
let wordsAdded;

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
			addWords();
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
};

function init() {
	wordlist = [];
	grid = [];
	
	for (let y = 0; y < GRID_LEN; y++) {
		grid.push([]);
		for (let x = 0; x < GRID_LEN; x++) {
			grid[y].push(BLANK_CHAR);
		}
		
	}
	
	//console.log(grid);
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
	
	printGrid(grid);
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
			delta = DIRECTIONS[ Object.keys(DIRECTIONS)[ Math.floor(Math.random() * DIRECTIONS_LEN)] ];
		//for (let delta in DIRECTIONS) {				//for each direction
			tRow = row;
			tCol = col;
			
			//console.log(grid[tRow]);
			
			//first, check if we can place it
			for (counter = 0; counter < word.length; counter++) {
				//if out of bounds
				if (tRow < 0 || tRow >= grid.length || tCol < 0 || tCol >= grid[0].length) break;
				
				//console.log(tRow);
				//console.log(grid[tRow]);
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
			
			//console.log(grid);
			//printGrid(grid);
			return true;
		}
	}
	
	return false;
}


init();
//addSingleWord();
transmit();
//document.getElementById("input").addEventListener('input', transmit);
