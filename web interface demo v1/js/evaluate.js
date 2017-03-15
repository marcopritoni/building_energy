//data format: {"title":{},"predition":{}},r^2-val
//data formating not working yet

var main = function() {
	$.getJSON("/python.json", function(response){

		$("body").append("<h1>Python says :</h1>");
		response.forEach(function(print){
			$("body").append("<p>"+print+"</p>");
		})
	});



  (function(){
    $.getJSON("/python.json",  function (response) {
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
          text : 'Ghausi_ChilledWater_Demand_kBtu'
        },

        series : [{
          name : 'Ghausi_ChilledWater_Demand_kBtu',//data[0][0]
          data : realdata,
          tooltip: {
            valueDecimals: 2
          }
        }, {
          name : 'predition',//data[1][0]
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
