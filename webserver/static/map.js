// function myMap() {
//   var mapProp= {
//       center:new google.maps.LatLng(39.8097343, -98.5556199),
//       zoom:4,
//   };
//   var map = new google.maps.Map(document.getElementById("googleMap"),mapProp);

//   fetch("/selfreporteddata")
//   .then(data => data.json())
//   .then(data => {
//     Object.entries(data).forEach(([key, value]) => {
//       console.log(value);
//       addMarker(new google.maps.LatLng(value[1][0], value[1][1]), map, value[0]);
//     });
//   })

//   addMarker()
// }

// function addMarker(location, map, label) {
//   // Add the marker at the clicked location, and add the next-available label
//   // from the array of alphabetical characters.
//   new google.maps.Marker({
//     position: location,
//     label: label,
//     map: map,
//   });
// }

google.charts.load('current', {
  packages:['geochart'],
  mapsApiKey: 'AIzaSyCOjBlneiz6modsQUWGeGi0sFhXyQgN8pU'
});
google.charts.setOnLoadCallback(drawRegionsMap);

function drawRegionsMap() {
  var data = google.visualization.arrayToDataTable([
    ['State', 'Popularity'],
    ['New York', 22],
    ['New Jersey', 19],
    ['Montana', 20]
  ]);

  var options = {
    region: 'US',
    colorAxis: {
      colors: ['green', 'blue', 'yellow'],
      values: [19, 20, 22]
    },
    dataMode: 'markers',
    resolution: 'states',
    legend: 'none'
  };

  var chart = new google.visualization.GeoChart(document.getElementById('googleMap'));
  chart.draw(data, options);
}

const testData = async (map) => {

}