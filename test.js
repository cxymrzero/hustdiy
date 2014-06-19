var page = require('webpage').create();

page.open("http://localhost:8080/last", function    (status) {
    if (status !== 'success') {
        console.log('Unable to load the address!');
    } else {
        window.setTimeout(function () {
            // Heres the actual difference from your code...
            var bb = page.evaluate(function () { 
                return document.getElementsByClassName("wrapper")[0].getBoundingClientRect(); 
            });

            page.clipRect = {
                top:    bb.top,
                left:   bb.left,
                width:  bb.width,
                height: bb.height//675//
            };

            page.render('people.png');
            phantom.exit();
        }, 200);
    }
});