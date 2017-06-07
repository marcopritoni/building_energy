buildings = {};
Papa.parse("/BuildingSensors.csv", { 
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

			// Used to check if new building has the same sensor, then this option will stay selected
			old_sensor = $("#sel_val2").find('option:selected').text();

			$("#sel_val2").empty();
			$("#sel_val2").append('<option value="">Select a Building*</option>');
			sensors.forEach(function(sensor) {
				// If new building has same sensor type, that option stays selected through the building change
				var old_selected = false;
				if(sensor.sensor == old_sensor) { old_selected = true }
				var option = new Option(sensor.sensor, sensor.sensor.split(" ").join(""), false, old_selected);
				$("#sel_val2").append($(option))
			})
			// Change trigger makes sure text displays correctly
			$("#sel_val2").trigger("change");
		})
	}
});