var initialLocation;
var siberia = new google.maps.LatLng(60, 105);
var newyork = new google.maps.LatLng(40.69847032728747, -73.9514422416687);
var browserSupportFlag =  new Boolean();
var markersArray = [];
var businessesOnMap = {}
var infowindow = new google.maps.InfoWindow();;

function addBusToMap(bus,map,position)
{
    if(bus.businessID in businessesOnMap)
    {
        return;
    }
    var busLatLng = new google.maps.LatLng(bus.latitude,bus.longitude);
    var marker = new google.maps.Marker({
      position: busLatLng,
      map: map,
      title:bus.businessName
    });

    google.maps.event.addListener(marker, 'click', function() {
        var link = '/business/'+bus.businessID+'/?uname=none&password=generated_password&deviceID=_webbrowser&lat='+position.coords.latitude+'&lon='+position.coords.longitude;
        infowindow.setContent('<div>' + bus.businessName + ' recommendation of ' + bus.ratingRecommendation + '</div><a href="'+link+'"><img src="'+bus.photoLargeURL+'" /></a></div></div>');
        infowindow.open(map,marker);
    });
    businessesOnMap[bus.businessID] = marker;

}

function handleMapResponse(data,map,position)
{
    var result = data.result;
    var businesses = result.businesses;
    for (var i = 0; i < businesses.length; i++) { 
        addBusToMap(businesses[i],map,position);
    }   
}
function setMapPoints(map,position)
{

    var bds = map.getBounds();
              var minx = bds.getSouthWest().lat()
              var miny = bds.getSouthWest().lng()
              var maxx = bds.getNorthEast().lat()
              var maxy = bds.getNorthEast().lng()
              var dat = {uname : 'none', password: 'generated_password', deviceID: '_webbrowser', lat:position.coords.latitude, lon:position.coords.longitude, min_x:minx,min_y:miny, max_x:maxx, max_y:maxy};
              $.ajax({
                type: 'GET',
                url: 'api/businesses/map/',
                data: dat,
                success: function(data){    
                    handleMapResponse(data,map,position);
                },
                error: function(xhr, type){
                    alert(xhr);
                    alert('Ajax error!')
                }
              });    
}


function initializeExploreMap() {
  var myOptions = {
    zoom: 16,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };
  var map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
  
  // Try W3C Geolocation (Preferred)
  if(navigator.geolocation) {
    browserSupportFlag = true;
    navigator.geolocation.getCurrentPosition(function(position) {
            initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
            map.setCenter(initialLocation);
            google.maps.event.addListener(map, 'idle', function() {
                //1 seconds after the center of the map has changed, reload data
                window.setTimeout(function() {
                    setMapPoints(map,position);
                    }, 2000);
                });
            }, function() {
      handleNoGeolocation(browserSupportFlag);
    });
  }
  // Browser doesn't support Geolocation
  else {
    browserSupportFlag = false;
    handleNoGeolocation(browserSupportFlag);
  }
  
  function handleNoGeolocation(errorFlag) {
    if (errorFlag == true) {
      alert("Geolocation service failed.");
      initialLocation = newyork;
    } else {
      alert("Your browser doesn't support geolocation. We've placed you in Siberia.");
      initialLocation = siberia;
    }
    map.setCenter(initialLocation);
  }
}

window.onload = initializeExploreMap;
