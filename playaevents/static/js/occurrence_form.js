$(document).ready(function() {
	if($("#all_day").val() == "true") {
		$('#id_start_time_1').hide();
		$('#end-row').hide();
		$("label[for='id_start_time_0']").text('Day');
	}
});
