var wordlist = [];
var transmit = function() {

  $.ajax({
    url: 'http://www.randomtext.me/api/gibberish/p-1/100',
    type: 'GET',
    success: function(d) {
	var randomwords = d["text_out"].replace("<p>","").replace("</p>","").toUpperCase();
	//console.log(randomwords);
	construct_list(randomwords,10,4,8);
    } //end success callback
  });//end ajax call
}; //end transmit function

var construct_list = function (s,num,min,max){
    var list = s.split(" ");
    //console.log(list);
    for (i in list){
	//console.log(list[i]);
	if(wordlist.length < num && list[i].length <= max && list[i].length >=min && wordlist.indexOf(list[i]) == -1){
	    wordlist.push(list[i]);
	}
    }
    console.log(wordlist);
};

transmit();
//document.getElementById("input").addEventListener('input', transmit);
