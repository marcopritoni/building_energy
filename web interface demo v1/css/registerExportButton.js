function registerExportButton (chart, button) {
	var csvdata = [];
	csvdata.push(chart.series[0].xData); // Timestamps are first column, all series should share these so just pull it from first entry

	chart.series.slice(0,-1).forEach(function(series){ // The series array also includes a series 
																										 // for the scrollable navigation line of the chart,
																										 // slicing out the last entry will ignore this
		csvdata.push(series.yData);																									 
	})

	//csvdata now is an array with arrays for each column we will want in our csv
	var csv = "Timestamps";
	for (var i=1; i<=csvdata.length; i++) {

		csv += ",Series"+i;
	}
	csv += "\n"

	for (var i=0; i<csvdata[0].length; i++) {
		var row = [];
		for (var j=0; j<csvdata.length; j++) {
			row.push(csvdata[j][i]);
		}
		csv += row.join(',');
		csv += "\n";
	}

	var hiddenElement = document.createElement('a');
	hiddenElement.href = 'data:text/csv;charset=utf-8,'+encodeURI(csv);
	hiddenElement.target = '_blank';
	hiddenElement.download = 'CSVExport.csv';
	hiddenElement.click();

}