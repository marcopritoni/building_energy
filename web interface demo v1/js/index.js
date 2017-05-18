/*building dropdown menu - JQuery*/
$( "#sel_val1" ).change(function() {
  var option = $(this).find('option:selected').val();
  $('#sel_txt1').text(option);
});

/*fuel dropdown menu - JQuery*/
$( "#sel_val2" ).change(function() {
  var option = $(this).find('option:selected').val();
  $('#sel_txt2').text(option);
});


//Date Range Validation Function --JavaScript //check if the input dates are valid
var bindDateRangeValidation = function (f, s, e) {
    if(!(f instanceof jQuery)){
			console.log("Not passing a jQuery object");
    }

    var jqForm = f,
        startDateId = s,
        endDateId = e;

    var checkDateRange = function (startDate, endDate) {
        var isValid = (startDate != "" && endDate != "") ? startDate <= endDate : true;
        return isValid;
    }

    var bindValidator = function () {
        var bstpValidate = jqForm.data('bootstrapValidator');
        var validateFields = {
            startDate: {
                validators: {
                    notEmpty: { message: 'This field is required.' },
                    callback: {
                        message: 'Start Date must less than or equal to End Date.',
                        callback: function (startDate, validator, $field) {
                            return checkDateRange(startDate, $('#' + endDateId).val())
                        }
                    }
                }
            },
            endDate: {
                validators: {
                    notEmpty: { message: 'This field is required.' },
                    callback: {
                        message: 'End Date must greater than or equal to Start Date.',
                        callback: function (endDate, validator, $field) {
                            return checkDateRange($('#' + startDateId).val(), endDate);
                        }
                    }
                }
            },
          	customize: {
                validators: {
                    customize: { message: 'customize.' }
                }
            }
        }
        if (!bstpValidate) {
            jqForm.bootstrapValidator({
                excluded: [':disabled'],
            })
        }

        jqForm.bootstrapValidator('addField', startDateId, validateFields.startDate);
        jqForm.bootstrapValidator('addField', endDateId, validateFields.endDate);

    };

    var hookValidatorEvt = function () {
        var dateBlur = function (e, bundleDateId, action) {
            jqForm.bootstrapValidator('revalidateField', e.target.id);
        }

        $('#' + startDateId).on("dp.change dp.update blur", function (e) {
            $('#' + endDateId).data("DateTimePicker").setMinDate(e.date);
            dateBlur(e, endDateId);
        });

        $('#' + endDateId).on("dp.change dp.update blur", function (e) {
            $('#' + startDateId).data("DateTimePicker").setMaxDate(e.date);
            dateBlur(e, startDateId);
        });
    }

    bindValidator();
    hookValidatorEvt();
};


//baseline1 period --JQuery
$(function () {
    var sd = new Date(2015, 0, 1), ed = new Date(2015, 5, 30);

    $('#startDate').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: sd,
      maxDate: ed
    });

    $('#endDate').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: ed,
      minDate: sd
    });

    //passing 1.jquery form object, 2.start date dom Id, 3.end date dom Id
    bindDateRangeValidation($("#form"), 'startDate', 'endDate');
});


// baseline2 period --JQuery
$(function () {
    var sd = new Date(2015, 6, 1), ed = new Date(2015, 11, 31);

    $('#startDate2').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: sd,
      maxDate: ed
    });

    $('#endDate2').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: ed,
      minDate: sd
    });

    //passing 1.jquery form object, 2.start date dom Id, 3.end date dom Id
    bindDateRangeValidation($("#form2"), 'startDate2', 'endDate2');
});


// evaluation period --JQuery
$(function () {
    var sd = new Date(2016, 0, 1), ed = new Date(2016, 11, 31);

    $('#startDate3').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: sd,
      maxDate: ed
    });

    $('#endDate3').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: ed,
      minDate: sd
    });

    //passing 1.jquery form object, 2.start date dom Id, 3.end date dom Id
    bindDateRangeValidation($("#form3"), 'startDate3', 'endDate3');
});

// Optional --JQuery
$(function () {
    var sd = new Date(2016, 0, 1), ed = new Date(2016, 11, 1);

    $('#startDate4').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: sd,
      maxDate: ed
    });

    $('#endDate4').datetimepicker({
      pickTime: false,
      format: "YYYY/MM/DD",
      defaultDate: ed,
      minDate: sd
    });

    //passing 1.jquery form object, 2.till date dom Id
    bindDateRangeValidation($("#form4"), 'startDate4', 'endDate4');
});

/*model dropdown menu - JQuery*/
$( "#sel_val3" ).change(function() {
  var option = $(this).find('option:selected').val();
  $('#sel_txt3').text(option);
});


var TMYMode = false;
$("#TMYSwitch").click(function() {
  if (!TMYMode) {
    $(this).removeClass("btn-default");
    $(this).addClass("active");
    $(this).addClass("btn-primary");

    $(".defaultRow").hide();
    $(".TMYRow").show();

    TMYMode = true;
  }
  else{
    $(this).removeClass("btn-primary");
    $(this).removeClass("active");
    $(this).addClass("btn-default");

    $(".TMYRow").hide();
    $(".defaultRow").show();

    TMYMode = false;
  }
})

var hidden = false;
$( "#dropdown" ).click(function() {
  if (!hidden){

    if (TMYMode) {
      $(".TMYRow, .headerRow, #evaluate").animate({opacity:0}, {start: function(){ $(this).hide(400) }});
      // $(this).parent().parent().siblings()
    }
    else {
      $(".defaultRow, .headerRow, #evaluate").animate({opacity:0}, {start: function(){ $(this).hide(400) }});
    }
    hidden = true;
  }
  else{
    if (TMYMode) {
      $(".TMYRow, .headerRow, #evaluate").animate({opacity:1}, {start: function(){ $(this).show(400) }});
    }
    else {
      $(".defaultRow, .headerRow, #evaluate").animate({opacity:1}, {start: function(){ $(this).show(400) }});
    }

    // $(this).parent().parent().siblings().animate({opacity:1}, {start: function(){ $(this).show(400) }});
    hidden = false;
  }
});

//side-bar
$(document).ready(function(){
$(".side-bar-button").click(function() {
  var shown = $(".side-bar").css("opacity");

  if(shown == 0){
    $(".side-bar").css("opacity", "1");
    $(".side-bar-button").attr("src","image/cross.png");
    $(".side-bar-button").css("margin-left", "30vh");
    //alert("The paragraph was clicked.");
  }
  if(shown == 1){
    $(".side-bar").css("opacity", "0");
    $(".side-bar-button").attr("src","image/ham.png");
    $(".side-bar-button").css("margin-left", "5vh");
    //alert("The paragraph was clicked.");
  }

});
});
