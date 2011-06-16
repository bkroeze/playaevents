/*jslint browser:true,undef:true,eqeqeq:false,nomen:true,white:false,plusplus:false,onevar:true */
/*global $,log,logging,window */

function textCounter(textarea, countdown, maxlimit)
{
    var left = maxlimit - textarea.value.length;
    if(textarea.value.length >= maxlimit) {
        textarea.value = textarea.value.substring(0, maxlimit);
        countdown.text(left + " Characters Available");
    } else {
        countdown.text(left + " Characters Available");
    }
}

// given the all_day checkbox, appropriately hide or show related rows
function allDayState(all_day_box) {
    if($(all_day_box).is(':checked')) {
        $('#id_start_time_1').hide();
        $('#id_end_time_1').hide();
        $("label[for='id_start_time_0']").text('Day');
        if($("#id_repeats").is(':checked')) {
            $('#start-row').hide();
            $('#end-row').hide();
        } else {
            $('#end-row').hide();
        }
    } else {
        $('#id_start_time_1').show();
        $('#id_end_time_1').show();
        $('#start-row').show();
        $('#end-row').show();
        $("label[for='id_start_time_0']").text('Start');
        if($("#id_repeats").is(':checked')) {
            $('#id_start_time_0').hide();
            $('#id_end_time_0').hide();
        } else {
            $('#id_start_time_0').show();
            $('#id_end_time_0').show();
        }
    }

}

function event_sync_dates() {
    var val, elt;

    val = $('#id_start_time_0').val();
    $("#id_end_time_0").val(val);
    $("select").sb('refresh');

}

$(document).ready(function() {

    if($("#existing").val() == "true") {
        if($("#id_repeats").is(':checked')) {
            $('#repeat-days-row').show();
        } else {
            $('#repeat-days-row').hide();
        }
        allDayState($("#id_all_day"));
    } else {
        $('#repeat-days-row').hide();
    }

    $("#id_repeats").click(function () {
        if(this.checked) {
            $('#repeat-days-row').show();
            $('#id_start_time_0').hide();
            $('#id_end_time_0').hide();
            if($("#id_all_day").is(':checked')) {
                $('#start-row').hide();
                $('#end-row').hide();
            }
        } else {
            $('#repeat-days-row').hide();
            $('#id_start_time_0').show();
            $('#id_end_time_0').show();
            $('#start-row').show();
            if($("#id_all_day").is(':checked')) {
            } else {
                $('#end-row').show();
            }
        }
    });

    $("#id_all_day").click(function () {
        allDayState(this);
    });

    $("#id_start_time_0").change(event_sync_dates);

    $("#id_print_description").keyup(function(){
        textCounter(this, $("#print_description_countdown"), 150);
    });

    $("#id_description").keyup(function(){
        textCounter(this, $("#online_description_countdown"), 2000);
    });

    $("#id_password_hint").keyup(function(){
        textCounter(this, $("#password_hint_countdown"), 120);
    });

});
