MAIN_URL = "http://localhost:8080/"

$(document).ready(function(){
    $("#task-input").focus();
    
    $("li").mouseover(function() {
        $(this).css("background-color", "#EEE");
        theElement = this;
        class_id = $(this).attr("class");
    });
    $("li").mouseout(function() {
        $(this).css("background-color", "white");
    });
    $("#complete-by-input").datepicker();
    $("#advanced-task-link").click(function(event) {
        event.preventDefault();
        $("#advanced-task-form").slideToggle();
        return false;
    });
    
    $("#ajax-message p").ajaxSend(function (event, request, settings){
        if (settings.url == MAIN_URL + "taskit/ajax/delete") {
            $(this).text("Deleting task...");
        }
        else if (settings.url == MAIN_URL + "taskit/ajax/complete") {
            $(this).text("Completing task...");
        }
        else if (settings.url == MAIN_URL + "taskit/ajax/sort-name" ||
                 settings.url == MAIN_URL + "taskit/ajax/sort-date") {
            $(this).text("Sorting tasks...");
            $("#your-tasks").slideUp(100);
        }
        $(this).css("visibility", "visible");
    });
    
    $("#ajax-message p").ajaxComplete(function (event, request, settings){
        if (settings.url == MAIN_URL + "taskit/ajax/sort-name" ||
            settings.url == MAIN_URL + "taskit/ajax/sort-date"){
            $("#your-tasks").slideDown('fast');
        }
        $(this).css("visibility", "hidden");
        $("#task-input").focus();
    });
    
    // Ajax calls for delete and complete links
    deleteComplete = $("#task-list li a").click(function(event) {
        event.preventDefault();
        var command = $(this).text();
        var link = this;
        var class_id = $(this).attr("class");
        var confirmed = true;
        if (command == "Delete it") {
            command = "delete";
            confirmed = confirm("Are you sure you want to delete this task?");
        }
        else if (command == "Complete it") {command = "complete"}
        if (confirmed){
        $.ajax({
            type: "POST",
            url: MAIN_URL + "taskit/ajax/"+command,
            data: "id="+class_id+"&command="+command,
            success: function(msg) {
                if (command == "delete") {
                    $("."+class_id+":first").slideUp();
                }
                else if (command == "complete") {
                    $(link).hide();
                    $("."+class_id + " span:first").css("text-decoration", "line-through");
                }
            }
        });
        }
    });
    
    //Ajax call for task sorting
    $("#sort-links li a").click(function(event) {
        event.preventDefault();
        var command = $(this).attr("class");
        $.ajax({
            type: "POST",
            url: MAIN_URL + "taskit/ajax/"+command,
            success: function(data) {
                $("#your-tasks").html(data);
            }
        });
    });
    
    // Ajax call for form submission
    $("#task-form").submit(function(event) {
        event.preventDefault();
        var jsonData = $("form#task-form").serialize();
        $.ajax({
            type: "POST",
            url: MAIN_URL + "taskit/ajax/submit-task",
            data: jsonData,
            error: function(data) {
                alert("Unable to add task.");
            },
            success: function(data) {
                $("#your-tasks").append(data)
            }
        });
    });
    
    deleteComplete();
});