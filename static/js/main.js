$( document ).ready(function() {
    
    loadBackground(jQuery('.bg').data('background'));

    jQuery(".catalog-categories a").hover(function(){
      if(jQuery(this).data('background')){
    	 loadBackground(jQuery(this).data('background'));
      }
      else{
        loadBackground(jQuery('.bg').data('background'));
      }
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