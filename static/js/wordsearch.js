"use strict";

let wordlist, grid;

const GRID_LEN = 6;
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

function transmit() {

  $.ajax({
    url: 'http://www.randomtext.me/api/gibberish/p-1/100',
    type: 'GET',
    success: function(d) {
	let randomwords = d["text_out"].replace("<p>","").replace("</p>","").toUpperCase();
	//console.log(randomwords);
	constructList(randomwords,10,4,8);
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
			grid[y].push("-");
		}
		
	}
	
	console.log(grid);
}

function addSingleWord(word, row, col, direction){
	let counter;
	let tRow, tCol; 
	let runs = word;
	for (	let turn = 0;
			turn < 2;
			runs = new StringBuilder(word).reverse().toString(), turn++) {
		if ((mData[row].length - col) < runs.length()) continue;
	
			try {
				tRow = row;
				tCol = col;
				counter = 0;
				for (counter = 0; counter < runs.length(); counter++) {
					if (mData[tRow][tCol] != '_' && 
						mData[tRow][tCol] != runs.charAt(counter)) {
						break;
					}
					tRow += direction.getDeltaY();
					tCol += direction.getDeltaX();
				}
			}
			catch(ArrayIndexOutOfBoundsException e) {
				return false;
			}
	
		if (counter == runs.length()) {
			for (counter = 0; counter < runs.length(); counter++) {
				mData[row][col] = runs.charAt(counter);
				col += direction.getDeltaX();
					row += direction.getDeltaY();
			}
			return true;
		}
		else continue;
	}
	return false;
}


init();
//transmit();
//document.getElementById("input").addEventListener('input', transmit);
