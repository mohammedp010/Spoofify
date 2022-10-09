function getItems() {
    $.ajax({
        url: _spPageContextInfo.webAbsoluteUrl + "/getArtist",
        type: "GET",
        headers: {
            "accept": "*/*",
        },
        success: function(data) {
            var response = data.d.results;
            $.each(response, function(key, value){
                $("#artistList").append('<option value="' + value + '">' + value +'</option>');
            });
            console.log(data);
        },
        
        error: function(error) {
            alert(JSON.stringify(error));
        }
    });
}