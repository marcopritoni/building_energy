function calculateTotalSavings (timestamps, data) {
	var total = 0;
	for (i=1; i < timestamps.length; i++){
		var time_window = timestamps[i] - timestamps[i-1];
		var usage = data[i];
		normalized_period_usage = time_window * usage / 3600000 / 1000; // UNITS are kBtu*hr
		total = total + normalized_period_usage; 		
	}
	return total;
}