var main = function() {
	$.getJSON("/python.json", function(response){
		$("body").append("<h1>Python says :</h1>");
		response.forEach(function(print){
			$("body").append("<p>"+print+"</p>");
		})
	});
};

document.getElementById("evaluate").onclick = main;