    var  route_map = L.map('random_route').setView([55.8642, -4.2518], 11);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiY29ubm9yMjExMCIsImEiOiJjanJzN3l1czcwY2d1NDltaWlzbDBhdzY1In0.dog8eflpKvUl4vpVJ0oCjA'
    }).addTo(route_map);

     var  pop_map = L.map('most_pop').setView([pop[0][2][0], pop[0][2][1]], 11);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiY29ubm9yMjExMCIsImEiOiJjanJzN3l1czcwY2d1NDltaWlzbDBhdzY1In0.dog8eflpKvUl4vpVJ0oCjA'
    }).addTo(pop_map);

    var x;
    var activ;
    var url;
    var data;
    var name;
    name = String(pop[0][0]);
    activ = `https://www.strava.com/activities/${pop[0][1]}`;
    url = `<a href= ${activ}>View Route</a>`;
    data = "time: " + String(pop[0][5]) + "<br> elevation: " + String(pop[0][4]) + "m<br> distance: " + String((pop[0][3] / 1000).toFixed(2)) + "km";
    L.marker([pop[0][2][0], pop[0][2][1]]).addTo(pop_map).bindPopup("<strong>" + name + "</strong><br>" + "<p>" + data + "</p><br>" + url);




