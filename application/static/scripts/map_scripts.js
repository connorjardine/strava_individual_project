// The first parameter are the coordinates of the center of the map
    // The second parameter is the zoom level
    var map = L.map('map').setView([55.8642, -4.2518], 11);

    L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}', {
        attribution: 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
        maxZoom: 18,
        id: 'mapbox.streets',
        accessToken: 'pk.eyJ1IjoiY29ubm9yMjExMCIsImEiOiJjanJzN3l1czcwY2d1NDltaWlzbDBhdzY1In0.dog8eflpKvUl4vpVJ0oCjA'
    }).addTo(map);

    var theMarker = {};
    var theCircle = {};
    var lat = {};
    var lon = {};

    map.on('click', function (e) {
        lat = e.latlng.lat;
        lon = e.latlng.lng;

        console.log("You clicked the map at LAT: " + lat + " and LONG: " + lon);
        //Clear existing marker,

        if (theMarker !== undefined) {
            map.removeLayer(theMarker);
            map.removeLayer(theCircle);
        }
        ;

        //Add a marker to show where you clicked.
        theMarker = L.marker([lat, lon]).addTo(map);
        theCircle = L.circle([lat, lon], 10000).addTo(map);
    });

    $(function () {
        $("#slider-dist").slider({
            range: true,
            min: 0,
            max: 100,
            values: [1, 20],
            slide: function (event, ui) {
                $("#amount").val("$" + ui.values[0] + " - $" + ui.values[1]);
            }
        });
        $("#amount").val($("#slider-dist").slider("values", 0) +
            "km - " + $("#slider-dist").slider("values", 1) + "km");
    });

    $(function () {
        $("#slider-elev").slider({
            range: true,
            min: 0,
            max: 1500,
            values: [0, 200],
            slide: function (event, ui) {
                $("#amount1").val("$" + ui.values[0] + " - $" + ui.values[1]);
            }
        });
        $("#amount1").val($("#slider-elev").slider("values", 0) +
            "m - " + $("#slider-elev").slider("values", 1) + "m");
        console.log($("#slider-elev").slider("values", 0));
    });

