    $(function() {
      $.getJSON($SCRIPT_ROOT + '/_get_task_status', function(data) {
          console.log(data.result);
          if (data.result === "COMPLETE") {
              $("#result").text("Run parsing is complete.").addClass("alert alert-success").attr('data-role', 'alert');
              $.getJSON($SCRIPT_ROOT + '/_update_task_status')
          }
          else if (data.result === "RUNNING") {
              $("#result").text("Parsing runs.").addClass("alert alert-primary").attr('data-role', 'alert');
          }
          else {
              $("#result").empty();
          }
      });
    setInterval( function() {
      $.getJSON($SCRIPT_ROOT + '/_get_task_status', function(data) {
          console.log(data.result);
          if (data.result === "COMPLETE") {
              $("#result").text("Run parsing is complete.");
              $.getJSON($SCRIPT_ROOT + '/_update_task_status')
          }
          else if (data.result === "RUNNING") {
              $("#result").text("Parsing runs.");
          }
          else {
             $("#result").empty();
          }
      });
      return false;
    }, 5000);
  });

