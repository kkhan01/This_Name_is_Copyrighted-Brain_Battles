var transmit = function( e ) {

  $.ajax({
    url: 'http://www.randomtext.me/api/gibberish/p-1/30',
    type: 'GET',
    data: {'text' : input },
    success: function(d) {
      console.log(d);
      console.log(JSON.parse(d));
    } //end success callback
  });//end ajax call
  console.log('goodbye');
}; //end transmit function

transmit(e);
//document.getElementById("input").addEventListener('input', transmit);
