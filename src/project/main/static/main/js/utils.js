function setElementVisible(id) {
    "use strict";
    if ($("#" + id).hasClass("invisible")) {
        $("#" + id).removeClass("invisible").addClass("visible");
    } else if ($("#" + id).hasClass("visible")) {
        $("#" + id).removeClass("visible").addClass("invisible");
    }
}


// using jQuery
function getCookie(name) {
    "use strict";
    var cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        var cookies = document.cookie.split(";");
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    "use strict";
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function postAjax(url, operation, property, value, callback) {
    "use strict";
    var csrftoken = $("[name='csrfmiddlewaretoken']").attr("value");
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    $.ajax({
        type: "POST",
        url: url,
        dataType: "json",
        data: {
            query: JSON.stringify({
                "operation": operation,
                "property": property,
                "value": value
            })
        },
        success: function (data) {
            if ($.isFunction(callback)) {
                callback(data);
            }
        },
        error: function (data) {
            alert("Sorry, this is a wrong parameter");
        }
    });
}
