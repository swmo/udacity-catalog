$( document ).ready(function() {
    

    loadBackground(jQuery('.bg').data('background'));


   // jQuery(".bg").css("background-image","url('"+jQuery('.bg').data('background') +"')").done(function(){jQuery('.bg-loader').hide()})

    jQuery(".catalog-categories a").hover(function(){
    	console.log(jQuery(this).data('background'));
    	loadBackground('https://images.pexels.com/photos/848612/pexels-photo-848612.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940');
    },function(){
		loadBackground(jQuery('.bg').data('background'));
    });


   function loadBackground(background){
		jQuery('.bg-loader').fadeIn(0);
		jQuery('<img/>').attr('src', background).on('load', function() {
		   jQuery(this).remove(); // prevent memory leaks as @benweet suggested
		   jQuery('.bg').css('background-image', 'url('+background+')');
		   jQuery('.bg-loader').fadeOut(800);
		});
    }
});