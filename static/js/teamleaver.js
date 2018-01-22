var leavebutton = document.getElementById("leave");
var teamname = document.getElementsByTagName("h1")[0].innerHTML.split(" ")[2];


var leaveTeam = function(e){

    var li = this.parentElement.parentElement.parentElement;
    var kicked = li.childNodes[1].childNodes[1].childNodes[1].innerHTML;
    $.ajax({
	url: '/delete_member',
	data : { member: kicked, team : teamname},
	type: 'POST',
	success: function(d) {
	    console.log(d);
	} //end success callback
    });//end ajax call
    window.location.href = "/home";
}


leavebutton.addEventListener("click", leaveTeam);
