    $(function() {
      $.getJSON($SCRIPT_ROOT + '/_get_task_status', function(data) {
          console.log(data.result);
          if (data.result === "COMPLETE") {
              setTimeout(
                function()
                {
                    $("#result").text("Run parsing is complete.").css({"background-color":"#2a333c", "display": "block"});
                    $("#result-container").css({"display": "none"});
                    $.getJSON($SCRIPT_ROOT + '/_update_task_status');
                }, 5000);
                $("#result").css({"display": "none"});
                $("#result-container").css({"display": "none"})
          }
          else if (data.result === "RUNNING") {
              $("#result").text("Parsing runs.").css({"background-color":"#2a333c", "display": "block"});
              $("#result-container").css({"display": "block"})
          }
          else {
              $("#result").css({"display": "none"});
              $("#result-container").css({"display": "none"})
          }
      });
    setInterval( function() {
      $.getJSON($SCRIPT_ROOT + '/_get_task_status', function(data) {
          console.log(data.result);
          if (data.result === "COMPLETE") {
            setTimeout(
                function()
                {
                    $("#result").text("Run parsing is complete.").css({"background-color":"#2a333c", "display": "block"});
                    $("#result-container").css({"display": "block"});
                    $.getJSON($SCRIPT_ROOT + '/_update_task_status');
                }, 5000);
                $("#result").css({"display": "none"});
                $("#result-container").css({"display": "none"})
          }
          else if (data.result === "RUNNING") {
              $("#result").text("Parsing runs.").css({"background-color":"#2a333c", "display": "block"});
              $("#result-container").css({"display": "block"})
          }
          else {
             $("#result").css({"display": "none"});
             $("#result-container").css({"display": "none"})
          }
      });
      return false;
    }, 5000);
  });

