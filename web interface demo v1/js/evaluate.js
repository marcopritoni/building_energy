//data format: {"title":{},"predition":{}},r^2-val
//data formating not working yet

var main = function() {
	document.getElementById("loader").style.display="block";


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
	modeltype = $('#sel_val3').val();
	parameters['modeltype'] = modeltype;

  (function(){

    $.getJSON("/python.json", parameters, function (response) {
      document.getElementById("loader").style.display="none";
      if (!response.error) {
        console.log("No error!");
        console.log(response);
        $("#dropdown").click();
        var tmy_mode_on = $("#TMYSwitch").hasClass("active");
        if (tmy_mode_on){
          $(".defchart").css("display", "none");
          $(".tmychart").css("display", "block");
          $(".tmychart").css("border", "2px solid black");
        }
        else{
          $(".tmychart").css("display", "none");
          $(".defchart").css("display", "block");
          $(".defchart").css("border", "2px solid black");
        }

  			var model1stats = JSON.parse(response[3]);
  			$("#modelStats #R2").text(model1stats["Adj_R2"].toFixed(2));
  			$("#modelStats #cvrmse").text(model1stats["CV_RMSE"].toFixed(2));
  			$("#modelStats #nmbe").text(model1stats["NMBE"].toFixed(2));
  			$("#modelStats #rmse").text(model1stats["RMSE"].toFixed(2));

  			var data = [];
  			var ghausi = JSON.parse(response[0]);
  			for (var key in ghausi) {
  				if (ghausi.hasOwnProperty(key)) {
  					data.push([key, ghausi[key]]);
  				}
  			}
  			var realdata = [];
  			var real = data[0][1];
  			for (var key in real) {
  				if (real.hasOwnProperty(key)) {
  					realdata.push([parseInt(key), real[key]]);
  				}
  			}
  			var preditiondata = [];
  			var predition = data[1][1];
  			for (var key in predition) {
  				if (predition.hasOwnProperty(key)) {
  					preditiondata.push([parseInt(key), predition[key]]);
  				}
  			}
        $('#highstock').highcharts('StockChart', {
          rangeSelector : {
            selected : 1
          },
          xAxis: {
            gridLineWidth: 1
          },
          title : {
            text : "Model Against Baseline 1"
          },
          legend : {
          	enabled: true
          },
          series : [{
            name : data[0][0],
            data : realdata,
            tooltip: {
              valueDecimals: 2
            },
            color : "green"
          }, {
            name : data[1][0],
            data : preditiondata,
            tooltip: {
              valueDecimals: 2
            },
            color: "red"
          }]
        });

        if (tmy_mode_on){
          var model2stats = JSON.parse(response[7]);
          $("#modelStats2 #R2").text(model2stats["Adj_R2"].toFixed(2));
          $("#modelStats2 #cvrmse").text(model2stats["CV_RMSE"].toFixed(2));
          $("#modelStats2 #nmbe").text(model2stats["NMBE"].toFixed(2));
          $("#modelStats2 #rmse").text(model2stats["RMSE"].toFixed(2));

          var data6 = [];
          var ghausi6 = JSON.parse(response[4]);
          for (var key in ghausi6) {
            if (ghausi6.hasOwnProperty(key)) {
              data6.push([key, ghausi6[key]]);
            }
          }
          var realdata = [];
          var real = data6[0][1];
          for (var key in real) {
            if (real.hasOwnProperty(key)) {
              realdata.push([parseInt(key), real[key]]);
            }
          }
          var preditiondata = [];
          var predition = data6[1][1];
          for (var key in predition) {
            if (predition.hasOwnProperty(key)) {
              preditiondata.push([parseInt(key), predition[key]]);
            }
          }
          $('#highstock2').highcharts('StockChart', {
            rangeSelector : {
              selected : 1
            },
            xAxis: {
              gridLineWidth: 1
            },
            title : {
              text : "Model2 Against Baseline 2"
            },
            legend : {
              enabled: true
            },
            series : [{
              name : data6[0][0],
              data : realdata,
              tooltip: {
                valueDecimals: 2
              },
              color : "green"
            }, {
              name : data6[1][0],
              data : preditiondata,
              tooltip: {
                valueDecimals: 2
              },
              color: "red"
            }]
          });
        }

        if (!tmy_mode_on){
          var data2 = [];
          var ghausi2 = JSON.parse(response[1]);
    			for (var key in ghausi2) {
    				if (ghausi2.hasOwnProperty(key)) {
    					data2.push([key, ghausi2[key]]);
    				}
    			}
    			var realdata = [];
    			var real = data2[0][1];
    			for (var key in real) {
    				if (real.hasOwnProperty(key)) {
    					realdata.push([parseInt(key), real[key]]);
    				}
    			}
    			var preditiondata = [];
    			var predition = data2[1][1];
    			for (var key in predition) {
    				if (predition.hasOwnProperty(key)) {
    					preditiondata.push([parseInt(key), predition[key]]);
    				}
    			}

          $('#highstock3').highcharts('StockChart', {
            rangeSelector : {
              selected : 1
            },
            xAxis: {
              gridLineWidth: 1
            },
            title : {
              text : "Model Against Evaluation Period"
            },
            legend : {
            	enabled : true
            },
            series : [{
              name : data2[0][0],
              data : realdata,
              tooltip: {
                valueDecimals: 2
              },
              color : "green"
            }, {
              name : data2[1][0],
              data : preditiondata,
              tooltip: {
                valueDecimals: 2
              },
              color : "red"
            }]
          });


          var data3 = [];
          var ghausi3 = JSON.parse(response[2]);
    			for (var key in ghausi3) {
    				if (ghausi3.hasOwnProperty(key)) {
    					data3.push([parseInt(key), ghausi3[key]]);
    				}
    			}

          $('#highstock4').highcharts('StockChart', {

          	chart : {
          		events : {
          			redraw: function(){
          				shownTimestamps = this.series[0].processedXData;
          				shownData = this.series[0].processedYData;
          				var savingsTotal = calculateTotalSavings(shownTimestamps, shownData);
          				$("#savings").text(savingsTotal.toFixed(2)+" kBtu*hr");
          			}
          		}
          	},
            rangeSelector : {
              selected : 1
            },
            xAxis: {
              gridLineWidth: 1
            },
            title : {
              text : "Savings"
            },
            legend : {
            	enabled : true
            },
            series : [{
              name : "Savings",
              data : data3,
              tooltip: {
                valueDecimals: 2
              },
              color : "gold"
            }]
          });

          var savingsChart = $('#highstock4').highcharts();
          var startTimestamps = savingsChart.series[0].processedXData;
          var startData = savingsChart.series[0].processedYData;
          var savingsTotal = calculateTotalSavings(startTimestamps, startData);
          $("#savings").text(savingsTotal.toFixed(2)+" kBtu*hr");
        }


        if (tmy_mode_on){
          var data7 = [];
          var ghausi7 = JSON.parse(response[8]);
          for (var key in ghausi7) {
            if (ghausi7.hasOwnProperty(key)) {
              data7.push([key, ghausi7[key]]);
            }
          }
          var realdata = [];
          var real = data7[0][1];
          for (var key in real) {
            if (real.hasOwnProperty(key)) {
              realdata.push([parseInt(key), real[key]]);
            }
          }
          var preditiondata = [];
          var predition = data7[1][1];
          for (var key in predition) {
            if (predition.hasOwnProperty(key)) {
              preditiondata.push([parseInt(key), predition[key]]);
            }
          }

          $('#highstock5').highcharts('StockChart', {
            rangeSelector : {
              selected : 1
            },
            xAxis: {
              gridLineWidth: 1
            },
            title : {
              text : "Model 1 Against Model 2 with TMY Input"
            },
            legend : {
              enabled : true
            },
            series : [{
              name : data7[0][0],
              data : realdata,
              tooltip: {
                valueDecimals: 2
              },
              color : "green"
            }, {
              name : data7[1][0],
              data : preditiondata,
              tooltip: {
                valueDecimals: 2
              },
              color : "red"
            }]
          });
        }
      }

      else { // ERROR RECEIVED
        alert("We ran into an error building your models, check that your settings are correct and try again.\n\n"+response.error);
      }
      


      
    });
  })();
};

document.getElementById("evaluate").onclick = main;
