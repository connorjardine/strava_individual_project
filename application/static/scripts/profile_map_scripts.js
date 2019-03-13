    var  rand_map = L.map('random_route').setView([rand[0][2][0], rand[0][2][1]], 11);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiY29ubm9yMjExMCIsImEiOiJjanJzN3l1czcwY2d1NDltaWlzbDBhdzY1In0.dog8eflpKvUl4vpVJ0oCjA'
    }).addTo(rand_map);

     var  pop_map = L.map('most_pop').setView([pop[0][2][0], pop[0][2][1]], 9);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiY29ubm9yMjExMCIsImEiOiJjanJzN3l1czcwY2d1NDltaWlzbDBhdzY1In0.dog8eflpKvUl4vpVJ0oCjA'
    }).addTo(pop_map);

    var activ;
    var url;
    var data;
    var name;
    for (var pop_x = 0; pop_x < pop.length; pop_x++) {
        name = String(pop[pop_x][0]);
        activ = `https://www.strava.com/activities/${pop[pop_x][1]}`;
        url = `<a href= ${activ} target="_blank">View Route</a>`;
        data = "Time: " + String(pop[pop_x][5]) + "<br> Elevation Gain: " + String(pop[pop_x][4]) + "m<br> Distance: " + String((pop[pop_x][3] / 1000).toFixed(2)) + "km";
        L.marker([pop[pop_x][2][0], pop[pop_x][2][1]]).addTo(pop_map).bindPopup("<strong>" + name + "</strong><br>" + "<p class='popup'>" + data + "</p><br>" + url).openPopup();
    }

    var rand_activ;
    var rand_url;
    var rand_data;
    var rand_name;
    rand_name = String(rand[0][0]);

    rand_activ = `https://www.strava.com/activities/${rand[0][1]}`;
    rand_url = `<a href= ${rand_activ} target="_blank">View Route</a>`;
    rand_data = "Time: " + String(rand[0][5]) + "<br> Elevation Gain: " + String(rand[0][4]) + "m<br> Distance: " + String((rand[0][3] / 1000).toFixed(2)) + "km";
    L.marker([rand[0][2][0], rand[0][2][1]]).addTo(rand_map).bindPopup("<strong>" + rand_name + "</strong><br>" + "<p class='popup'>" + rand_data + "</p><br>" + rand_url).openPopup();;

    $("#pop-label").text("Logged " + String(pop[0][6]) + " times.");




