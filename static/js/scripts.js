
// Select item from the side panel according to the page we are on
$(function(){
	var pathname = $(location).attr('pathname');
	$('ul#links a[href="'+pathname+'"]').parent().addClass("active");
});
