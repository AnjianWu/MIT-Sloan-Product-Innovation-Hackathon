


function check_aws(){
  data_packet = { type: "check_aws" }

  $.ajax({
    url: "receiver",
    type: 'POST',
    contentType: "application/json",
    dataType: 'json',
    success: function (response) {
      if (response["data"] != "none"){

        console.log("AWS SQS - "+response["data"]);

        if (response["data"] == "Start"){
          StartListening();
        }
        if (response["data"] == "Stop"){
          StopListening();
        }
      } 
    },
    data: JSON.stringify(data_packet) // Send the data packet
  });
}

// Send detected sentenses so far
function update_words(start_time, stop_time, sentense){

  data_packet = { type: "words",
                  t0:  start_time,
                  t1: stop_time,
                  words: sentense
                }

  $.ajax({
    url: "receiver",
    type: 'POST',
    contentType: "application/json",
    dataType: 'json',
    success: function (response) {

    },
    data: JSON.stringify(data_packet) // Send the data packet
  });
}


// Setup Checking AWS at Regular intervals

document.addEventListener('DOMContentLoaded', function () {

  setInterval(check_aws, 1000);

});

var processSpeech = function(transcript) {

  return true;
};