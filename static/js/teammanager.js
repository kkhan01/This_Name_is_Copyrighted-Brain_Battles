var input = document.getElementsByTagName("input")[1];
var kickbuttons = document.getElementsByClassName("kick");
var teamname = document.getElementsByTagName("h1")[0].innerHTML.split(" ")[2];
var adderbutton = document.getElementById("adderbutton");
var memberlist = document.getElementById("memberul");
var memberlistli = memberlist.childNodes[1];



var removeMember = function(e){
    
    var li = this.parentElement.parentElement.parentElement;
    console.log(li);
    console.log(li.childNodes[1].childNodes[1].childNodes[1]);
    var kicked = li.childNodes[1].childNodes[1].childNodes[1].innerHTML;
    $.ajax({
	url: '/delete_member',
	data : { member: kicked, team : teamname},
	type: 'POST',
	success: function(d) {
	    console.log(d);
	    li.parentElement.remove();
	} //end success callback
    });//end ajax call

    

};

var addMember = function(e){
    
    var userinput = input.value;
    var response = "string";

    $.ajax({
	url: '/new_member',
	data : { member: userinput, team : teamname},
	type: 'POST',
	async: false,
	success: function(d) {
	    response = d;
	    console.log(d);
	} //end success callback
    });//end ajax call
    if(response == "Done!"){
	console.log(response);
	var newmember = memberlistli.cloneNode(true);
	var newlink = newmember.childNodes[1].childNodes[1].childNodes[1].childNodes[1];
	newlink.innerHTML = userinput;
	newlink.setAttribute("href","/profile?user=" + userinput)
	var newbutton =  newmember.childNodes[1].childNodes[1].childNodes[3].childNodes[1];
	newbutton.innerHTML = "Kick";
	newbutton.setAttribute("class","kick button");
	console.log(newbutton);
	memberlist.appendChild(newmember);
	newbutton.addEventListener("click", removeMember);
    }

    
};

for (i = 0; i < kickbuttons.length; i++){
    if(kickbuttons[i].innerHTML.includes("Kick")){
	kickbuttons[i].addEventListener("click", removeMember);
    };
};
adderbutton.addEventListener("click", addMember);

