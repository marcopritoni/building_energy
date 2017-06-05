//data format: {"title":{},"predition":{}},r^2-val
//data formating not working yet

var main = function() {
	document.getElementById("loader").style.display="block";

  var tmy_mode_on = $("#TMYSwitch").hasClass("active");
	parameters = {};
  if (tmy_mode_on){
    parameters['parsetype'] = "tmy";
    parameters['building'] = ($('#sel_val1').val());
    parameters['energy'] = ($('#sel_val2').val());
    modeltype = $('#sel_val3').val();
    parameters['modeltype'] = modeltype;
    baseline1date = $('#startDate').val().split('/');
    parameters['base1start'] = (baseline1date.slice(0,2).join('-'));
    baseline1date2 = $('#endDate').val().split('/');
    parameters['base1end'] = (baseline1date2.slice(0,2).join('-'));
    baseline2date = $('#startDate2').val().split('/');
    parameters['base2start'] = (baseline2date.slice(0,2).join('-'));
    baseline2date2 = $('#endDate2').val().split('/');
    parameters['base2end'] = (baseline2date2.slice(0,2).join('-'));
    predictdate = $('#startDate4').val().split('/');
    parameters['predictstart'] = (predictdate.slice(0,2).join('-'));
    predictdate2 = $('#endDate4').val().split('/');
    parameters['predictend'] = (predictdate2.slice(0,2).join('-'));
  }
  else{
    parameters['parsetype'] = "simple"
    parameters['building'] = ($('#sel_val1').val());
    parameters['energy'] = ($('#sel_val2').val());
    modeltype = $('#sel_val3').val();
    parameters['modeltype'] = modeltype;
    baseline1date = $('#startDate').val().split('/');
    parameters['base1start'] = (baseline1date.slice(0,2).join('-'));
    baseline1date2 = $('#endDate').val().split('/');
    parameters['base1end'] = (baseline1date2.slice(0,2).join('-'));
    evaldate = $('#startDate3').val().split('/');
    parameters['evalstart'] = (evaldate.slice(0,2).join('-'));
    evaldate2 = $('#endDate3').val().split('/');
    parameters['evalend'] = (evaldate2.slice(0,2).join('-'));
  }

  (function(){

    $.getJSON("/python.json", parameters, function (response) {
      document.getElementById("loader").style.display="none";
      if (!response.error) {
        console.log("No error!");
        console.log(response);
        $("#dropdown").click();
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

        var parseResponse = function(response) {
          var output = {};
          var object = JSON.parse(response);
          for (var key in object) {
            if (object.hasOwnProperty(key)) {
              output[key] = []
              for (var kee in object[key]) {
                output[key].push([parseInt(kee), object[key][kee]]);
              }
            }
          }
          return output;
        }
        if (!tmy_mode_on){
          var test = parseResponse(response[0]);
          console.log(test);
    			
          var keys = Object.keys(test);
          $('#highstock').highcharts('StockChart', {
            rangeSelector : {
              selected : 1
            },
            xAxis: {
              gridLineWidth: 1
            },
            yAxis: [{ // OAT Axis
              labels: {
                format: '{value}°F',
              },
              opposite:false
            },
            { // Energy Use Axis

            }],
            title : {
              text : "Model Against Baseline 1"
            },
            legend : {
            	enabled: true
            },
            series : [{
              name : keys[0],
              data : test[keys[0]],
              tooltip: {
                valueDecimals: 2
              },
              yAxis:1,
              color : "green"
            }, {
              name : 'OAT',
              data : test[keys[1]],
              tooltip: {
                valueDecimals: 2
              },
              yAxis: 0,
              color: "#0088ff",
              visible:false
            },
            {
              name : keys[2],
              data : test[keys[2]],
              tooltip: {
                valueDecimals: 2
              },
              yAxis:1,
              color: "red"
            }]
          });

          var model1stats = JSON.parse(response[2]);
          $("#modelStats #R2").text(model1stats["Adj_R2"].toFixed(2));
          $("#modelStats #cvrmse").text(model1stats["CV_RMSE"].toFixed(2));
          $("#modelStats #nmbe").text(model1stats["NMBE"].toFixed(2));
          $("#modelStats #rmse").text(model1stats["RMSE"].toFixed(2));
          $("#modelStats #numpts").text(test[keys[2]].length);     

          var evaloutput = parseResponse(response[1]);
          var evalkeys = Object.keys(evaloutput);
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
              name : evalkeys[0],//data2[0][0],
              data : evaloutput[evalkeys[0]],//realdata,
              tooltip: {
                valueDecimals: 2
              },
              color : "green"
            }, {
              name : evalkeys[2],//data2[1][0],
              data : evaloutput[evalkeys[2]],//preditiondata,
              tooltip: {
                valueDecimals: 2
              },
              color : "red"
            }]
          });

          var data3 = parseResponse(response[1]);
          console.log(data3);
          var savkeys = Object.keys(data3);
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
              data : data3[savkeys[3]],
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
        else {
          console.log(response);
          var tmyresponse = parseResponse(response[0]);
          var tmykeys = Object.keys(tmyresponse);
          console.log(tmykeys);          
          // $('#highstock2').highcharts('StockChart', {
          //   rangeSelector : {
          //     selected : 1
          //   },
          //   xAxis: {
          //     gridLineWidth: 1
          //   },
          //   yAxis: [{ // OAT Axis
          //     labels: {
          //       format: '{value}°F',
          //     },
          //     opposite:false
          //   },
          //   { // Energy Use Axis

          //   }],
          //   title : {
          //     text : "Model2 Against Baseline 2"
          //   },
          //   legend : {
          //     enabled: true
          //   },
          //   series : [{
          //     name : tmykeys[2],
          //     data : tmyresponse[tmykeys[2]],
          //     tooltip: {
          //       valueDecimals: 2
          //     },
          //     yAxis: 1,
          //     color : "green"
          //   }, {
          //     name : 'OAT',
          //     data : tmyresponse["OAT"],
          //     tooltip: {
          //       valueDecimals: 2
          //     },
          //     yAxis: 0,
          //     color: "#0088ff",
          //     visible:false
          //   }, {
          //     name : "Baseline 2",
          //     data : tmyresponse["Baseline 2"],
          //     tooltip: {
          //       valueDecimals: 2
          //     },
          //     yAxis: 1,
          //     color: "red"
          //   }]
          // });

          // var model2stats = JSON.parse(response[7]);
          // $("#modelStats2 #R2").text(model2stats["Adj_R2"].toFixed(2));
          // $("#modelStats2 #cvrmse").text(model2stats["CV_RMSE"].toFixed(2));
          // $("#modelStats2 #nmbe").text(model2stats["NMBE"].toFixed(2));
          // $("#modelStats2 #rmse").text(model2stats["RMSE"].toFixed(2));
          // $("#modelStats2 #numpts").text(preditiondata.length); 


          $('#highstock5').highcharts('StockChart', {
            rangeSelector : {
              selected : 1
            },
            xAxis: {
              gridLineWidth: 1
            },
            yAxis: [{ // OAT Axis
              labels: {
                format: '{value}°F',
              },
              opposite:false
            },
            { // Energy Use Axis

            }],
            title : {
              text : "Model 1 Against Model 2 with TMY Input"
            },
            legend : {
              enabled : true
            },
            series : [{
              name : tmykeys[3],
              data : tmyresponse[tmykeys[3]],
              tooltip: {
                valueDecimals: 2
              },
              yAxis : 1,
              color : "green"
            }, {
              name : tmykeys[4],
              data : tmyresponse[tmykeys[4]],
              tooltip: {
                valueDecimals: 2
              },
              yAxis : 1,
              color : "red"
            }, {
              name : tmykeys[0],
              data : tmyresponse[tmykeys[0]],
              tooltip: {
                valueDecimals: 2
              },
              yAxis: 0,
              color: "#0088ff",
              visible:false 
            }]
          });
        }


        
      

        $(".chart").each(function(index, chart){
          var highchart = $(chart).find(".histock").highcharts();
          if (highchart)
            $(chart).find(".export").off("click");
            $(chart).find(".export").click(highchart,exportChartAsCSV);
        });
      }

      else { // ERROR RECEIVED
        alert("We ran into an error building your models, check that your settings are correct and try again.\n\n"+response.error);
      }
      


      
    });
  })();
};

document.getElementById("evaluate").onclick = main;
