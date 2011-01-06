MAIN_URL = "http://localhost:8080/taskit/";
TASK_LIMIT = 10;

$(document).ready(function(){
    var num_tasks = $("#task-list li").length
    $("#task-input").focus();
    $("#complete-by-input").datepicker();
    
    $("li").mouseover(function() {
        //$(this).css("background-color", "#EEE");
        theElement = this;
        class_id = $(this).attr("class");
    });
    $("li").mouseout(function() {
        //$(this).css("background-color", "white");
    });
    
    $("#advanced-task-link").click(function(event) {
        event.preventDefault();
        $("#advanced-task-form").slideToggle();
        return false;
    });
    
    $("#ajax-message p").ajaxSend(function (event, request, settings){
        if (settings.url == MAIN_URL + "ajax/delete") {
            $(this).text("Deleting task...");
        }
        else if (settings.url == MAIN_URL + "ajax/complete") {
            $(this).text("Completing task...");
        }
        /*else if (settings.url == MAIN_URL + "ajax/sort-name" ||
                 settings.url == MAIN_URL + "ajax/sort-date" ||
                 settings.url == MAIN_URL + "ajax/sort-completeby-date") {
            $(this).text("Sorting tasks...");
            $("#your-tasks").slideUp(100);
        }*/
        $(this).css("visibility", "visible");
    });
    
    $("#ajax-message p").ajaxComplete(function (event, request, settings){
        /*if (settings.url == MAIN_URL + "ajax/sort-name" ||
            settings.url == MAIN_URL + "ajax/sort-date" ||
            settings.url == MAIN_URL + "ajax/sort-completeby-date"){
            $("#your-tasks").slideDown('fast');
        }*/
        $(this).css("visibility", "hidden");
        $("#task-input").focus();
    });
    
    // Ajax calls for delete and complete links
    deleteComplete = function(event) {
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
            url: MAIN_URL + "ajax/"+command,
            data: "id="+class_id+"&command="+command,
            success: function(msg) {
                if (command == "delete") {
                    $("."+class_id+":first").slideUp();
                    num_tasks = num_tasks - 1;
                }
                else if (command == "complete") {
                    $(link).hide();
                    $("."+class_id + " span:first").css("text-decoration", "line-through");
                }
            }
        });
        }
    };
    $("#task-list li a").click(deleteComplete);
    
    //Ajax call for task sorting
    $(".extra-links li a").click(function(event) {
        event.preventDefault();
        var command = $(this).attr("class");
        $.ajax({
            type: "POST",
            url: MAIN_URL + "ajax/"+command,
            success: function(data) {
                $("#your-tasks").html(data);
            },
            beforeSend: function() {
                $("#ajax-message p").text("Sorting tasks...");
                $("#your-tasks").slideUp(100);
            },
            complete: function() {
                $("#your-tasks").slideDown('fast');
                $("#task-list li a").click(deleteComplete); //Need to rebind function
            },
            
        });
    });
    
    // Ajax call for form submission
    $("#task-form").submit(function(event) {
        if (num_tasks >= TASK_LIMIT) {
            alert("You have reached the maximum number of tasks.");
            return false;
        }
        event.preventDefault();
        var jsonData = $("form#task-form").serialize();
        $.ajax({
            type: "POST",
            url: MAIN_URL + "ajax/submit-task",
            data: jsonData,
            beforeSend: function() {
                $("#ajax-message p").text("Submitting task...");
            },
            error: function(data) {
                alert("Unable to add task.");
            },
            success: function(data) {
                num_tasks = num_tasks + 1;
                $("#advanced-task-form").slideUp(200);
                $("#task-list").append(data);
                $("#task-list li:last").css("display", "none");
                $("#task-list li:last").slideDown();
                $("#task-list li:last a").click(deleteComplete);
                $("#task-form").each (function() {
                    this.reset();
                });
            }
        });
    });
    
});