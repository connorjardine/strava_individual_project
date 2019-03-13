    $(function() {
      $.getJSON($SCRIPT_ROOT + '/_get_task_status', function(data) {
          console.log(data.result);
          if (data.result === "COMPLETE") {
              setTimeout(
                function()
                {
                    $("#result").text("Run parsing is complete.").css("background-color", "white");
                    $.getJSON($SCRIPT_ROOT + '/_update_task_status');
                }, 5000);
                $("#result").hide();
                $("#loader").hide()
          }
          else if (data.result === "RUNNING") {
              $("#result").text("Parsing runs.").css("background-color", "#cce5ff").show();
              $("#loader").show()
          }
          else {
              $("#result").hide();
              $("#loader").hide()
          }
      });
    setInterval( function() {
      $.getJSON($SCRIPT_ROOT + '/_get_task_status', function(data) {
          console.log(data.result);
          if (data.result === "COMPLETE") {
            setTimeout(
                function()
                {
                    $("#result").text("Run parsing is complete.").css("background-color", "white");
                    $.getJSON($SCRIPT_ROOT + '/_update_task_status');
                }, 5000);
                $("#result").hide();
                $("#loader").hide()
          }
          else if (data.result === "RUNNING") {
              $("#result").text("Parsing runs.").css("background-color", "#cce5ff").show();
              $("#loader").show()
          }
          else {
             $("#result").hide();
              $("#loader").hide()
          }
      });
      return false;
    }, 5000);
  });

