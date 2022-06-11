$(function(){
	$('button').click(function(){
		var name = $('#inputname').val();
		var city = $('#inputcity').val();
        var state = $('#inputstate').val();
        var phone = $('#inputphone').val();
        var genres = $('#inputgenres').val();
        var image_link = $('#inputimage_link').val();
        var facebook_link = $('#inputfacebook_link').val();
        var seeking_venue = $('#seeking_venue').val();
        var seeking_description = $('#seeking_description').val();
        
		$.ajax({
			url: '/venues/create',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
/*
<scripts>
document.getElementByClassName('form').onsubmit = function (e) {
   e.preventDefault();
   fetch('/venues/create', {
      method: 'POST',
              body: JSON.stringify({
              'name':document.getElement.ById('name').value
              'city':document.getElement.ById('city').value
              'state':document.getElement.ById('state').value
              'phone':document.getElement.ById('phone').value
              'genres':document.getElement.ById('genres').value
              'image_link':document.getElement.ById('image_link').value
              'facebook_link':document.getElement.ById('facebook_link').value
              'website_link':document.getElement.ById('website_link').value
              'seeking_talent':document.getElement.ById('seeking_talent').value
              'seeking_description':document.getElement.ById('seeking_description').value
                   }),
               headers: {
                        'Content-Type': 'application/json'
                       }
    })
</script>
\*