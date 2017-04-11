//data format: {"title":{},"predition":{}},r^2-val
//data formating not working yet

var main = function() {

	parameters = {};
	parameters['building'] = ($('#sel_val1').val());
	parameters['energy'] = ($('#sel_val2').val());
	baseline1date = $('#startDate').val().split('/');
	parameters['base1start'] = (baseline1date.slice(0,2).join('-'));
	baseline1date2 = $('#endDate').val().split('/');
	parameters['base1end'] = (baseline1date2.slice(0,2).join('-'));
	baseline2date = $('#startDate2').val().split('/');
	parameters['base2start'] = (baseline2date.slice(0,2).join('-'));
	baseline2date2 = $('#endDate2').val().split('/');
	parameters['base2end'] = (baseline2date2.slice(0,2).join('-'));
	evaldate = $('#startDate3').val().split('/');
	parameters['evalstart'] = (evaldate.slice(0,2).join('-'));
	evaldate2 = $('#endDate3').val().split('/');
	parameters['evalend'] = (evaldate2.slice(0,2).join('-'));
	predictdate = $('#startDate4').val().split('/');
	parameters['predictstart'] = (predictdate.slice(0,2).join('-'));
	predictdate2 = $('#endDate4').val().split('/');
	parameters['predictend'] = (predictdate2.slice(0,2).join('-'));

  (function(){
  	
    $.getJSON("/python.json", parameters, function (response) {
			console.log(response);
			var data = [];
			var ghausi = JSON.parse(response[0]);
			for (var key in ghausi) {
				if (ghausi.hasOwnProperty(key)) {
					data.push([key, ghausi[key]]);
				}
			}
			console.log(data[0][1]);
			var realdata = [];
			var real = data[0][1];
			for (var key in real) {
				if (real.hasOwnProperty(key)) {
					realdata.push([parseInt(key), real[key]]);
				}
			}
			console.log(realdata);
			var preditiondata = [];
			var predition = data[1][1];
			for (var key in predition) {
				if (predition.hasOwnProperty(key)) {
					preditiondata.push([parseInt(key), predition[key]]);
				}
			}
			console.log(preditiondata);
      $('.highstock').highcharts('StockChart', {
        rangeSelector : {
          selected : 1
        },
        xAxis: {
          gridLineWidth: 1
        },
        title : {
          text : data[0][0]
        },

        series : [{
          name : data[0][0],
          data : realdata,
          tooltip: {
            valueDecimals: 2
          }
        }, {
          name : 'prediction',//data[1][0]
          data : preditiondata,
          tooltip: {
            valueDecimals: 2
          }
        }]
      });
    });
  })();
};

document.getElementById("evaluate").onclick = main;
