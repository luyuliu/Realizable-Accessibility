$("#sidebar-hide-btn").click(function () {
  animateSidebar();
  $('.mini-submenu').fadeIn();
  return false;
});


$('.mini-submenu').on('click', function () {
  animateSidebar();
  $('.mini-submenu').hide();
})

function animateSidebar() {
  $("#sidebar").animate({
    width: "toggle"
  }, 350, function () {
    map.invalidateSize();
  });
}


var baseLayer = L.esri.basemapLayer('Topographic')
map = L.map("map", {
  zoom: 13,
  center: [39.98, -83],
  layers: [baseLayer],
  zoomControl: false,
  attributionControl: false,
  maxZoom: 18
});

function createCORSRequest(method, url) {
  var xhr = new XMLHttpRequest();
  if ("withCredentials" in xhr) {
    xhr.open(method, url, true);

  } else if (typeof XDomainRequest != "undefined") {
    xhr = new XDomainRequest();
    xhr.open(method, url);

  } else {
    xhr = null;

  }
  return xhr;
}

function calculateDistance(self, latlng1, latlng2) {
  R = 6373
  lat1 = float(latlng1[0])
  lon1 = float(latlng1[1])
  lat2 = float(latlng2[0])
  lon2 = float(latlng2[1])
  pi = 3.1415926

  theta = lon1 - lon2
  radtheta = pi * theta / 180
  radlat1 = pi * lat1 / 180
  radlat2 = pi * lat2 / 180

  dist = Math.sin(radlat1) * Math.sin(radlat2) + Math.cos(radlat1) * Math.cos(radlat2) * Math.cos(radtheta)
  try {
    dist = Math.acos(dist)
  }
  catch (err) {
    dist = 0
  }
  dist = dist * 180 / pi * 60 * 1.1515 * 1609.344 / 1.4

  return dist

}

var scooterIcon = L.icon({
  iconUrl: './img/s.svg',
  iconSize: [20, 20], // size of the icon
});

var stopIcon = L.icon({
  iconUrl: './img/stop.png',
  iconSize: [20, 20], // size of the icon
})

var electronicIcon = L.icon({
  iconUrl: './img/e.png',
  iconSize: [20, 20], // size of the icon
});

$("#add-btn").click(function () {
  $("#time-input").val(parseInt($("#time-input").val()) + 120)
});

var select = document.getElementById("stop-select");
var options = ['MOREASS', 'HIGCOON', '4TH15TN', 'TREZOLS', 'KARPAUN', 'LIVGRAE', 'GRESHEW', 'MAIOHIW', 'AGL540W', 'WHIJAEE', '3RDCAMW', 'HARZETS', 'MAIBRICE', 'SAI2NDS', '3RDMAIS', 'STYCHAS', 'LOC230N', 'BETDIEW', 'STEMCCS', 'INNWESE', 'HANMAIN', 'HIGINDN', '4THCHIN', 'RIDSOME', 'KARHUYN', 'LIVBURE', 'LONWINE', 'MAICHAW', 'BROHAMIW', 'WHI3RDE', '1STLINW', 'MAINOEW', 'MAIIDLE', '5THCLEE', '3RDTOWS', 'STYGAMS', 'KOE113W', 'TAM464S', 'CAS150S', 'BROOUTE', 'ALUGLENS', 'FRABREN', 'SOU340N', 'HILTINS', 'STRHOVE', 'SAWCOPN', 'HAMWORN', 'DALDUBN', 'MCNCHEN', 'HILBEAS', 'NOROWEN', 'SOUTER2A', 'GENSHAN', 'VACLINIC', 'MORHEATE', 'KOEEDSW1', 'TRAMCKW', 'FAISOUN', 'SAWSAWN', 'CLIHOLE', 'CHAMARN', 'CLE24THN']

for (var i = 0; i < options.length; i++) {
  var opt = options[i];
  var el = document.createElement("option");
  el.textContent = opt;
  el.value = opt;
  select.appendChild(el);
}

normalMarkers = []
scooterMarkers = []
scooterLocationMarker = []
scooterLocationFlag = false
startStop = null
queryStop = null


timeBudget = 60 * 60
theTimeStamp = 1561932000
theScooterDate = "20190630"

$("#start-btn").click(function () {
  todayDate = $("#date-input").val().replace('-', '').replace('-', '')
  console.log(todayDate)
  timestamp = parseInt($("#time-input").val())

  $.get('http://127.0.0.1:50022/lime_location?where={"ts":' + timestamp + '}', function (rawstops) {
    stops = rawstops._items
    console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      if (stop.type_name == "scooter") {
        var point = L.marker([stop.latitude, stop.longitude], { icon: scooterIcon }).addTo(map);
      }
      else {
        var point = L.marker([stop.latitude, stop.longitude], { icon: electronicIcon }).addTo(map);
      }
      point.bindPopup("<b>Meter range: " + stop.meter_range + "</b><br><b>Battery level: " + stop.battery_level + "</b><br><b>Last Three: " + stop.last_three + "</b>")

    }

  });
});

$("#scooter-btn").click(scooterButtonEvent);

function scooterButtonEvent() {
  // todayDate = $("#cota-date-input").val().replace('-', '').replace('-', '')
  // console.log(todayDate)
  // timestamp = parseInt($("#cota-time-input").val())
  timestamp = theTimeStamp
  timeDeltaLimit = timeBudget;
  walkingSpeed = 1.4
  walkingDistanceLimit = 700
  walkingTimeLimit = walkingDistanceLimit / walkingSpeed
  startStopID = $("#stop-select").val()
  console.log("Start", startStopID)
  var queryURL = 'http://127.0.0.1:20196/abtest_scooter_' + timestamp + '?where={"startStopID":"' + startStopID + '"}'
  console.log(queryURL)
  $.get(queryURL, function (rawstops) {
    stops = rawstops._items
    // console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var radius = (timeDeltaLimit - (stop.time)) * walkingSpeed / 20

      if (radius < 0) {
        radius = 0
      }
      if (radius > walkingDistanceLimit) {
        radius = walkingDistanceLimit
      }
      // console.log(stop)
      // console.log(stop.accessible_stop_id, radius)
      var marker1 = L.circle([stop.stop_lat, stop.stop_lon], {
        color: "red",
        radius: radius,
        stroke: 0,
        opacity: 1
      }).addTo(map);
      marker1.bindPopup("<b>stop ID: " + stop.receivingStopID + "</b><br><b>busTime: " + stop.busTime + "</b><br><b>scooterTime: " + stop.scooterTime + "</b><br><b>walkTime: " + stop.walkTime + "</b><br><b>firstScooterIncrement: " + stop.firstScooterIncrement + "</b><br><b>firstmile scooter ID: " + stop.firstScooterID + "</b> " + "<br><b>lastmile scooter increment: " + stop.lastmileScooterID + "</b>" + "<br><b>lastmile scooter ID: " + stop.lastmileScooterIncrement + "</b>" + "<br><b>time: " + stop.time + "</b>")
      scooterMarkers.push(marker1)
    }

  });
}

$("#normal-btn").click(normalButtonEvent);

function normalButtonEvent() {
  // todayDate = $("#cota-date-input").val().replace('-', '').replace('-', '')
  // console.log(todayDate)
  // timestamp = parseInt($("#cota-time-input").val())
  timestamp = theTimeStamp;
  timeDeltaLimit = timeBudget;
  walkingSpeed = 1.4
  walkingDistanceLimit = 700
  walkingTimeLimit = walkingDistanceLimit / walkingSpeed
  console.log("Start")
  startStopID = $("#stop-select").val()
  var queryURL = 'http://127.0.0.1:20196/abtest_normal_' + timestamp + '?where={"startStopID":"' + startStopID + '"}'
  console.log(queryURL)
  $.get(queryURL, function (rawstops) {
    stops = rawstops._items
    // console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var radius = (timeDeltaLimit - (stop.time)) * walkingSpeed / 20

      if (radius < 0) {
        radius = 0
      }
      if (radius > walkingDistanceLimit) {
        radius = walkingDistanceLimit
      }
      // console.log(stop.stop_id, radius)
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        radius: radius,
        stroke: 0,
        opacity: 1
      }).addTo(map);
      marker.bindPopup("<b>stop ID: " + stop.accessible_stop_id + "</b><br><b>busTime: " + stop.busTime + "</b><br><b>scooterTime: " + stop.scooterTime + "</b><br><b>walkTime: " + stop.walkTime + "</b><br><b>transferTime: " + stop.transferTime + "</b><br><b>firstmile scooter ID: " + stop.firstmileScooterID + "</b> " + "<br><b>lastmile scooter ID: " + stop.lastmileScooterID + "</b>" + "<br><b>time: " + stop.time + "</b>")
      normalMarkers.push(marker)

      if (stop.accessible_stop_id == startStopID) {
        console.log("Add Icon")
        startStop = L.marker([stop.stop_lat, stop.stop_lon], { icon: stopIcon }).addTo(map);
      }
    }

  });
}

function scooterVisualization() {
  timestamp = theTimeStamp
  var url = 'http://127.0.0.1:50022/' + theScooterDate + '?where={"ts":' + timestamp + '}';
  console.log(url)
  $.get(url, function (rawstops) {
    stops = rawstops._items
    console.log(stops)

    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var point = L.marker([stop.latitude, stop.longitude], { icon: scooterIcon }).addTo(map);
      point.bindPopup("<b>ID: " + stop.new_id + "</b><br><b>Battery level: " + stop.meter_range + "</b>")
      scooterLocationMarker.push(point);

    }

  });
}

// $('#stop-select').change(function () {
//   removeMarker();
//   scooterButtonEvent();
//   normalButtonEvent();
//   if (!scooterLocationFlag) {
//     scooterVisualization();
//     scooterLocationFlag = true;
//   }
//   document.getElementById("scooter-checkbox").checked = true;
//   document.getElementById("normal-checkbox").checked = true;

// })

function removeMarker() {
  for (var i = 0; i < normalMarkers.length; i++) {
    map.removeLayer(normalMarkers[i])
  }
  for (var i = 0; i < scooterMarkers.length; i++) {
    map.removeLayer(scooterMarkers[i])
  }
  try {
    map.removeLayer(startStop)
  }
  catch (e) {
  }
}

$("#scooter-checkbox").click(function () {
  if ($(this).is(':checked')) {
    console.log("scooter open!")
    for (var i = 0; i < normalMarkers.length; i++) {
      scooterMarkers[i].setStyle({
        fillOpacity: 0.2
      })
    }
  } else {
    for (var i = 0; i < normalMarkers.length; i++) {
      scooterMarkers[i].setStyle({
        fillOpacity: 0
      })
    }
  }
});

$("#normal-checkbox").click(function () {
  if ($(this).is(':checked')) {
    console.log("scooter open!")
    for (var i = 0; i < normalMarkers.length; i++) {
      normalMarkers[i].setStyle({
        fillOpacity: 0.2
      })
    }

  } else {
    console.log("scooter close!")
    for (var i = 0; i < normalMarkers.length; i++) {
      normalMarkers[i].setStyle({
        fillOpacity: 0
      })
    }

  }
});

$("#scooterlocation-checkbox").click(function () {
  if ($(this).is(':checked')) {
    console.log("scooterlocation open!")
    for (var i = 0; i < scooterLocationMarker.length; i++) {
      scooterLocationMarker[i].setStyle({
        fillOpacity: 1
      })
    }

  } else {
    console.log("scooterlocation close!")
    for (var i = 0; i < scooterLocationMarker.length; i++) {
      scooterLocationMarker[i].setStyle({
        fillOpacity: 0
      })
    }

  }
});

$('#stop-input').keypress(function (e) {
  if (e.which == 13) {
    var stop_id = $("#stop-input").val();
    var queryURL = 'http://127.0.0.1:5555/1559154545_stops?where={"stop_id":"' + stop_id + '"}'
    $.get(queryURL, function (rawstops) {
      var stop = rawstops._items[0];
      console.log(stop)
      try {
        map.removeLayer(queryStop)
      }
      catch (e) {
      }
      queryStop = L.marker([stop.stop_lat, stop.stop_lon], { icon: stopIcon }).addTo(map);


    });
  }
});

$('#show-tragectory-button').click(function () {
  var start_stop = $("#start-stop-input").val();
  // var start_stop = "3RDMAIS"
  var end_stop = $("#end-stop-input").val();
  var startTimestamp = 1532534400
  var queryURL = 'http://127.0.0.1:20190/rel_20180725_1532534400?where={"startStopID":"' + start_stop + '"}';
  
  // var queryURL = 'http://127.0.0.1:20191/20190904_1567598400?where={"startStopID":"' + start_stop + '"}';

  $.get(queryURL, function (rawstops) {
    var stops = rawstops._items;
    // console.log(stops)
    var stopsDic = {}
    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var receivingStopID = stop["receivingStopID"];
      stopsDic[receivingStopID] = stop;
    }

    var endPointID = end_stop;
    var count = 0;

    console.log(stopsDic[endPointID])
    // console.log(stopsDic[endPointID]["transferCountRT"], stopsDic[endPointID]["transferCountSC"])
    var transferCount = 0;
    var transferCountOG = 0;
    var lastTripID = stopsDic[endPointID]["lastTripIDRT"];
    var lastTripIDOG = stopsDic[endPointID]["lastTripIDSC"];


    while (true) {
      // console.log(stopsDic)
      var endPoint = stopsDic[endPointID];
      var endPointLatLng = [endPoint["stop_lat"], endPoint["stop_lon"]];


      if (lastTripID != endPoint["lastTripIDRT"] && endPoint["lastTripTypeRT"] == "bus") {
        transferCount += 1
        console.log(lastTripID, endPoint["lastTripIDRT"])
      }

      lastTripID = endPoint["lastTripIDRT"];

      var startPointID = stopsDic[endPointID]["generatingStopIDRT"];
      var startPoint = stopsDic[startPointID];
      if (startPoint == null) {
        break;
      }
      var startPointLatLng = [startPoint["stop_lat"], startPoint["stop_lon"]];

      var latlngs = [
        startPointLatLng,
        endPointLatLng
      ];

      var polyline = L.polyline(latlngs, { color: 'red', weight: 9 }).addTo(map);
      polyline.bindPopup("<b>trip type: " + endPoint["lastTripTypeRT"] + "   " + endPoint["lastTripIDRT"] + " " + (endPoint["timeRT"] - startPoint["timeRT"]))
      endPointID = startPointID;


      var marker = L.circle([endPoint["stop_lat"], endPoint["stop_lon"]], {
        radius: 100,
        color: "red"
      }).addTo(map);
      ``
      marker.bindPopup(endPoint["receivingStopID"] + ", " + (endPoint["timeRT"] + startTimestamp) + "," + "RT" + count)

      count++;
      if (count > 2000) {
        break
      }
    }

    var endPointID = end_stop;
    var count = 0;
    while (true) {
      // console.log(stopsDic)
      var endPoint = stopsDic[endPointID];
      var endPointLatLng = [endPoint["stop_lat"], endPoint["stop_lon"]];


      if (lastTripIDOG != endPoint["lastTripIDSC"] && endPoint["lastTripTypeSC"] == "bus") {
        transferCountOG += 1
        console.log(lastTripID, endPoint["lastTripIDSC"])
      }
      lastTripIDOG = endPoint["lastTripIDSC"];

      var startPointID = stopsDic[endPointID]["generatingStopIDSC"];
      var startPoint = stopsDic[startPointID];
      if (startPoint == null) {
        break;
      }
      var startPointLatLng = [startPoint["stop_lat"], startPoint["stop_lon"]];

      var latlngs = [
        startPointLatLng,
        endPointLatLng
      ];

      var polyline = L.polyline(latlngs, { color: 'blue', weight: 4.5 }).addTo(map);

      polyline.bindPopup("<b>trip type: " + endPoint["lastTripTypeSC"] + "   " + endPoint["lastTripIDSC"] + " " + (endPoint["timeSC"] - startPoint["timeSC"]))
      endPointID = startPointID;

      var marker = L.circle([endPoint["stop_lat"], endPoint["stop_lon"]], {
        radius: 80
      }).addTo(map);

      marker.bindPopup(endPoint["receivingStopID"] + "," + (endPoint["timeSC"] + startTimestamp) + "," + "SC" + count)

      count++;
      if (count > 2000) {
        break
      }
    }

    console.log(transferCount, transferCountOG)
    var queryURL2 = 'http://127.0.0.1:5555/1517430037_stops?where={"stop_id":"' + start_stop + '"}'
    console.log(queryURL2)
    $.get(queryURL2, function (rawstops) {
      stop = rawstops._items[0]
      // console.log(stops)
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        radius: 700,
        stroke: 0,
        opacity: 1,
        color: "black"
      }).addTo(map);


    });

  })

})

// $('#stop-select').val('3RDMAIS').trigger('change');

function returnColor(value, colorRamp, colorCode) {
  var colorRamp = [0, 100, 300, 500, 1000, 2000, 3000, Infinity]
  var colorCode = ["#0080FF", "#5CAEA2", "#B9DC45", "#FFDC00", "#FF9700", "#FF2000", "#000000"]
  for (var i = 1; i < colorRamp.length; i++) {
    if (value >= colorRamp[i - 1] && value < colorRamp[i]) {
      return colorCode[i - 1]
    }
    else {
      continue;
    }
  }
  return
}

$("#show-travel-time-button").click(function () {
  sampledStopsList = ['MOREASS', 'HIGCOON', '4TH15TN', 'TREZOLS', 'KARPAUN', 'LIVGRAE', 'GRESHEW', 'MAIOHIW', 'AGL540W', 'WHIJAEE', '3RDCAMW', 'HARZETS', 'MAIBRICE', 'SAI2NDS', '3RDMAIS', 'STYCHAS', 'LOC230N', 'BETDIEW', 'STEMCCS', 'INNWESE', 'HANMAIN', 'HIGINDN', '4THCHIN', 'RIDSOME', 'KARHUYN', 'LIVBURE', 'LONWINE', 'MAICHAW', 'BROHAMIW', 'WHI3RDE', '1STLINW', 'MAINOEW', 'MAIIDLE', '5THCLEE', '3RDTOWS', 'STYGAMS', 'KOE113W', 'TAM464S', 'CAS150S', 'BROOUTE', 'ALUGLENS', 'FRABREN', 'SOU340N', 'HILTINS', 'STRHOVE', 'SAWCOPN', 'HAMWORN', 'DALDUBN', 'MCNCHEN', 'HILBEAS', 'NOROWEN', 'SOUTER2A', 'GENSHAN', 'VACLINIC', 'MORHEATE', 'KOEEDSW1', 'TRAMCKW', 'FAISOUN', 'SAWSAWN', 'CLIHOLE', 'CHAMARN', 'CLE24THN']
  var startStopID = $("#stop-select").val();
  // for (var i = 0; i < sampledStopsList.length; i++) {
  // var startStopID = sampledStopsList[i]
  var queryURL = 'http://127.0.0.1:20196/acctest_scooter_20190701_1561982400?where={"startStopID":"' + startStopID + '"}'
  console.log(queryURL)
  $.get(queryURL, function (rawstops) {
    var stops = rawstops._items
    // console.log(stops)
    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i]
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        color: returnColor(stop.time),
        radius: 200,
        stroke: 0,
        opacity: 1
      }).addTo(map);
    }


  });
  // }

})

$("#show-WATT-button").click(function () {
  sampledStopsList = ['MOREASS', 'HIGCOON', '4TH15TN', 'TREZOLS', 'KARPAUN', 'LIVGRAE', 'GRESHEW', 'MAIOHIW', 'AGL540W', 'WHIJAEE', '3RDCAMW', 'HARZETS', 'MAIBRICE', 'SAI2NDS', '3RDMAIS', 'STYCHAS', 'LOC230N', 'BETDIEW', 'STEMCCS', 'INNWESE', 'HANMAIN', 'HIGINDN', '4THCHIN', 'RIDSOME', 'KARHUYN', 'LIVBURE', 'LONWINE', 'MAICHAW', 'BROHAMIW', 'WHI3RDE', '1STLINW', 'MAINOEW', 'MAIIDLE', '5THCLEE', '3RDTOWS', 'STYGAMS', 'KOE113W', 'TAM464S', 'CAS150S', 'BROOUTE', 'ALUGLENS', 'FRABREN', 'SOU340N', 'HILTINS', 'STRHOVE', 'SAWCOPN', 'HAMWORN', 'DALDUBN', 'MCNCHEN', 'HILBEAS', 'NOROWEN', 'SOUTER2A', 'GENSHAN', 'VACLINIC', 'MORHEATE', 'KOEEDSW1', 'TRAMCKW', 'FAISOUN', 'SAWSAWN', 'CLIHOLE', 'CHAMARN', 'CLE24THN']
  var startStopID = $("#stop-select").val();
  // for (var i = 0; i < sampledStopsList.length; i++) {
  // var startStopID = sampledStopsList[i]

  // var colorRamp1 = [0, 500, 1000, 1500, 3000, 4500, 6000, Infinity]
  var colorRamp1 = [0, 250, 500, 1000, 1500, 3000, 6000, Infinity]
  var colorRamp1 = [0, 1000, 1500, 2000, 2500, 3000, 6000, Infinity]
  var colorCode1 = ["#0080FF", "#5CAEA2", "#B9DC45", "#FFDC00", "#FF9700", "#FF2000", "#000000"]
  var queryURL = 'http://127.0.0.1:20199/full_20190701_1561982400'
  console.log(queryURL)
  $.get(queryURL, function (rawstops) {
    var stops = rawstops._items
    // console.log(stops)
    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i]
      var marker = L.circle([stop.stop_lat, stop.stop_lon], {
        color: returnColor(stop.WATT, colorRamp1, colorCode1),
        radius: 100,
        stroke: 0,
        opacity: 1
      }).addTo(map);
      marker.bindPopup("<b>stop ID: " + stop.stop_id + ":" + (stop.WATT) + "_" + (stop.WATT_OG) + "</b>")

    }


  });
  // }

})

var marker_list_RT = new Array();
var marker_list_SC = new Array();

$("#stp-button").click(function () {
  var start_stop = $("#stop-input").val()
  var queryURL = 'http://127.0.0.1:20191/20180207_1518008400?where={"startStopID":"' + start_stop + '"}';
  var budget = $("#budget-input").val()

  $.get(queryURL, function (raw) {
    var stops = raw._items;
    for (var i = 0; i < stops.length; i++) {
      var stop = stops[i];
      var speed = 1.4;
      var actual_budget_RT = (budget * 60 - stop.timeRV) * speed; // meters
      var actual_budget_SC = (budget * 60 - stop.timeSC) * speed; // meters

      // var limit = 700; // meters
      var limit = 100; // meters
      if (actual_budget_RT > limit) {
        actual_budget_RT = limit
      }
      if (actual_budget_SC > limit) {
        actual_budget_SC = limit
      }
      if (actual_budget_SC < 0) {
        actual_budget_SC = 0
      }
      if (actual_budget_RT < 0) {
        actual_budget_RT = 0
      }

      if (actual_budget_RT > 0){
        var marker_RT = L.circle([stop.stop_lat, stop.stop_lon], {
          color: "red",
          radius: actual_budget_RT,
          stroke: 0,
          opacity: 1
        }).addTo(map);
        marker_RT.bindPopup("<b>stop ID: " + stop.stop_id + ":" + (stop.timeRV) + "_" + (stop.timeSC) + "</b>")
        marker_list_RT.push(marker_RT)
      }

      if (actual_budget_SC > 0){
        var marker_SC = L.circle([stop.stop_lat, stop.stop_lon], {
          color: "blue",
          radius: actual_budget_SC,
          stroke: 0,
          opacity: 1
        }).addTo(map);
        marker_SC.bindPopup("<b>stop ID: " + stop.stop_id + ":" + (stop.timeRV) + "_" + (stop.timeSC) + "</b>")
        marker_list_SC.push(marker_SC)
      }


    }
  })

})
  
$("#RT-checkbox").change(function () {
  if (document.getElementById('RT-checkbox').checked) {
    for (var i in marker_list_RT) {
      map.addLayer(marker_list_RT[i])
    }
  } else {
    for (var i in marker_list_RT) {
      map.removeLayer(marker_list_RT[i])
    }
  }
})

$("#SC-checkbox").change(function () {
  if (document.getElementById('SC-checkbox').checked) {
    for (var i in marker_list_SC) {
      map.addLayer(marker_list_SC[i])
    }
  } else {
    for (var i in marker_list_SC) {
      map.removeLayer(marker_list_SC[i])
    }
  }
})