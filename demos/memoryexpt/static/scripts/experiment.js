var uniqueWords= [];

$(document).ready(function() {
    // Print the consent form.
    $("#print-consent").click(function() {
        window.print();
    });

    // Consent to the experiment.
    $("#consent").click(function() {
        store.set("hit_id", getUrlParameter("hit_id"));
        store.set("worker_id", getUrlParameter("worker_id"));
        store.set("assignment_id", getUrlParameter("assignment_id"));
        store.set("mode", getUrlParameter("mode"));

        allow_exit();
        window.location.href = '/instructions/instructions-1';
    });

    // Consent to the experiment.
    $("#no-consent").click(function() {
        allow_exit();
        self.close();
    });

    // Proceed to the waiting room.
    $("#go-to-waiting-room").click(function() {
        allow_exit();
        window.location.href = '/waiting';
    });

    // $("#finish-reading").hide();
    //
    // // Finish reading the wordList
    // $("#finish-reading").click(function() {
    //     // move to chatroom
    //     $("#stimulus").hide();
    //     $("#fillertask-form").hide();
    //     $("#response-form").show();
    //     $("#send-message").removeClass("disabled");
    //     $("#send-message").html("Send");
    //     $("#reproduction").focus();
    //     get_transmissions(my_node_id);
    // });

    // Send a message.
    $("#send-message").click(function() {
        send_message();
    });

    // Leave the chatroom.
    $("#leave-chat").click(function() {
        leave_chatroom();
    });

    // Submit the questionnaire.
    $("#submit-questionnaire").click(function() {
        submitResponses();
        submitAssignment();
    });
});

// Create the agent.
create_agent = function () {
    reqwest({
        url: "/node/" + participant_id,
        method: "post",
        type: "json",
        success: function (resp) {
            my_node_id = resp.node.id;
            // display wordList
            getWordList(my_node_id);
        },
        error: function (err) {
            console.log(err);
            errorResponse = JSON.parse(err.response);
            if (errorResponse.hasOwnProperty("html")) {
                $("body").html(errorResponse.html);
            } else {
                allow_exit();
                go_to_page("questionnaire");
            }
        }
    });
};

getWordList = function() {

    reqwest({
        url: "/node/" + my_node_id + "/received_infos",
        method: "get",
        type: "json",
        success: function (resp) {
            var wordList = JSON.parse(resp.infos[0].contents);
            showWordList(wordList);
        },
        error: function (err) {
            console.log(err);
            errorResponse = JSON.parse(err.response);
            $('body').html(errorResponse.html);
        }
    });
};

showWordList = function (wl) {
    if (wl.length === 0){ // Show filler task.
        showFillerTask();

    } else { // Show the word.
        $("#wordlist").html(wl.pop());
        setTimeout(function () {
            showWordList(wl);
        }, 2000);
    }
};

showFillerTask = function () {

    $("#stimulus").hide();
    $("#fillertask-form").show();

    setTimeout(function(){
        showExperiment();
    }, 30000);
};

showExperiment = function () {
    $("#fillertask-form").hide();
    submitResponses();
    $("#response-form").show();
    $("#send-message").removeClass("disabled");
    $("#send-message").html("Send");
    $("#reproduction").focus();
    get_transmissions(my_node_id);
};

get_transmissions = function (my_node_id) {
    reqwest({
        url: "/node/" + my_node_id + "/transmissions",
        method: "get",
        type: "json",
        data: {
            status: "pending",
        },
        success: function (resp) {

          transmissions = resp.transmissions;
          for (var i = transmissions.length - 1; i >= 0; i--) {

            display_info(transmissions[i].info_id);

            }
        },
        error: function (err) {
            console.log(err);
            // errorResponse = JSON.parse(err.response);
            // $("body").html(errorResponse.html);
        },
        complete: function (err) {
            setTimeout(function(){
                get_transmissions(my_node_id);
            }, 1000);
        }
    });
};

display_info = function(info_id) {
    reqwest({
        url: "/info/" + my_node_id + "/" + info_id,
        method: "get",
        type: "json",
        success: function (resp) {
            var word = resp.info.contents.toLowerCase();
            // if word hasn't appeared before, load into unique array and display
            if (uniqueWords.indexOf(word)=== -1){
              uniqueWords.push(word);
              $("#reply").append("<p>" + word + "</p>");
            }
        },
        error: function (err) {
            console.log(err);
            errorResponse = JSON.parse(err.response);
            $("body").html(errorResponse.html);
        }
    });
};

send_message = function() {
    //$("#send-message").addClass("disabled");
    //$("#send-message").html("Sending...");

    response = $("#reproduction").val(); //typing box

      // don't let people submit an empty response
      if (response.length === 0){
      return;
      }

      // let people submit only if word doesn't have a space
      if (response.indexOf(' ') >= 0) {
        $("#send-message").removeClass("disabled");
        $("#send-message").html("Send");
        return;
      }

      // will not let you add a word that is non-unique
      if (uniqueWords.indexOf(response.toLowerCase())=== -1){
        uniqueWords.push(response.toLowerCase());
        $("#reply").append("<p style='color: #1693A5;'>" + response.toLowerCase() + "</p>");
      } else {
        $("#send-message").removeClass("disabled");
        $("#send-message").html("Send");
        return;
      }

    $("#reproduction").val("");
    $("#reproduction").focus();

    reqwest({
        url: "/info/" + my_node_id,
        method: "post",
        data: {
            contents: response,
            info_type: "Info",
        },
        success: function (resp) {
            $("#send-message").removeClass("disabled");
            $("#send-message").html("Send");
        }
    });
};

leave_chatroom = function() {
    allow_exit();
    go_to_page("questionnaire");
};

$(document).keypress(function (e) {
  if (e.which == 13) {
    $("#send-message").click();
    return false;
  }
});

// Send participants to the end if there are any infos.
killIfAnyInfos = function () {
    reqwest({
      url: "/info",
      method: "get",
      success: function (resp) {
        if (resp.info.count > 0) {
          allow_exit();
          go_to_page("questionnaire");
        }
      }
    });
};

quorum = 1e6;
getQuorum = function () {
    reqwest({
        url: "/experiment/quorum",
        method: "get",
        success: function (resp) {
            quorum = resp.quorum;
        }
    });
};

waitForQuorum = function () {

    // If we haven't gotten the quorum yet, get it.
    if (quorum >= (1e6-1)) {
        getQuorum();

    // If we haven't created a participant yet, hold tight.
    } else if (participant_id === undefined || participant_id === "undefined"){
        // Do nothing.
    }

    // Otherwise, see if we have enough participants to proceed.
    else {
        reqwest({
            url: "/summary",
            method: "get",
            success: function (resp) {
                summary = resp.summary;
                n = numReady(resp.summary);
                percent = Math.round((n/quorum)*100.0) + "%";
                $("#waiting-progress-bar").css("width", percent);
                $("#progress-percentage").text(percent);

                if (n >= quorum) {
                    allow_exit();
                    go_to_page("exp");
                }
            },
        });
    }

    setTimeout(function(){
        waitForQuorum();
    }, 1000);
};

numReady = function(summary) {
    for (var i = 0; i < summary.length; i++) {
        if (summary[i][0] == "working") {
            return summary[i][1];
        }
    }
};

// hack for Dallinger 2.0
submitResponses = function () {
      submitNextResponse(0);
 };
