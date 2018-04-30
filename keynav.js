document.addEventListener('keydown', function(event) {
    if(event.keyCode == 87) {
    	// W key
        window.open('welcome.html','_self')
    }
    else if(event.keyCode == 80) {
    	// P key
        window.open('processing.html','_self')
    } else if(event.keyCode == 82) {
    	// R key
        window.open('result.html','_self')
    }
});