/*****************************************************************/
/******** SPEECH RECOGNITION using Web Speech API****************/
/*****************************************************************/
//var debouncedProcessSpeech = _.debounce(processSpeech, 500);

var recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = true;
var final_transcript = '';

var displayed_text = "";

var start_time = 0;

var active = false;

recognition.onresult = function(event) {

  if (active){

    if (start_time == 0){
      start_time = Math.round((new Date()).getTime() / 100)/10;
    }

    var interim_transcript = '';

    for (var i = event.resultIndex; i < event.results.length; ++i) {
      if (event.results[i].isFinal) {
        final_transcript += event.results[i][0].transcript;

        document.getElementById("text_display").innerHTML = document.getElementById("text_display").innerHTML 
        + final_transcript + " ";


        stop_time = Math.round((new Date()).getTime() / 100)/10;
        console.log("Talking Duration = "+(stop_time - start_time));

        update_words(start_time, stop_time, final_transcript);

        // Reset Everything
        final_transcript = " ";
        start_time = 0;

      } else {
        interim_transcript += event.results[i][0].transcript;
        //console.log(event.results[i][0].transcript);
      }
    }

  }else{
    start_time = 0;
  }
  
};

// Restart recognition if it has stopped
recognition.onend = function(event) {
  setTimeout(function() {

      
    console.log("SPEECH DEBUG: ended");
    recognition.start();
  }, 50);
};
recognition.start();

function StartListening(){
  console.log("Start Listening on computer");
  document.getElementById("text_display").innerHTML = "";
  active = true;
}

function StopListening(){
  console.log("Stopped Listening on computer");
  active = false;

}
/*****************************************************************/
/******** END OF SPEECH RECOG SETUP ******************************/
/*****************************************************************/

