//Geolocate an Address
function geolocation(address) {
    var geocoder, marker, infowindow;
    if(!geocoder) {
        geocoder = new google.maps.Geocoder();
    }
    var geocoderRequest = {
        address: address
    };
    geocoder.geocode(geocoderRequest, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            //console.log(results[0].geometry.location)
            //map.setCenter(results[0].geometry.location);
            var center = [results[0].geometry.location.lat(), results[0].geometry.location.lng()]//newLatLng;//[47.6062, -122.3321]//[40.741895,-73.989308];
            var zoom = 15; //14
            map.setView(center, zoom);

        }
    });
}



//Search site and move map in its location
function moveCenter() {
    var sear_area = document.getElementById('seartxt').value;
    geolocation(sear_area);


}

