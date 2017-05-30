buildings = {};
Papa.parse("http://localhost:8000/BuildingSensors.csv", {
	download:true,
	complete:function(results){
		// Construct the builldings object for referencing building/sensor pairs
		results.data.forEach(function(row){
			building = row[0];
			sensor = row[1];
			if (!buildings[building]) {
				buildings[building] = [];
			}
			buildings[building].push( {sensor:sensor} );
		})

		console.log(buildings);
		// Add options to the building select for each unique building from the CSV
		Object.keys(buildings).forEach(function(key){
			var option = new Option(key, key);
			$("#sel_val1").append($(option));
		})
		// On change handler which will populate the sensor select based on the building chosen.
		$("#sel_val1").change(function() {
			var selected_building = $(this).find('option:selected').text();
			sensors = buildings[selected_building];
			$("#sel_val2").empty();
			$("#sel_val2").append('<option selected value="">Select a Building*</option>');
			sensors.forEach(function(sensor) {
				var option = new Option(sensor.sensor, sensor.sensor.split(" ").join(""));
				$("#sel_val2").append($(option))
			})
		})
	}
});