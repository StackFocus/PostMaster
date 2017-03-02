// Read a page's GET URL variables and return them as an associative array.
// Inspired from http://www.drupalden.co.uk/get-values-from-url-query-string-jquery
function getUrlVars() {
    var vars = {};
    var queryStartIndex = window.location.href.indexOf('?');
    if (queryStartIndex != -1) {
        var hashes = window.location.href.slice(queryStartIndex + 1).split('&');

        for (var i = 0; i < hashes.length; i++) {
            var hash = hashes[i].split('=');
            vars[hash[0]] = hash[1];
        }
    }

    return vars;
}


function changePage(obj, e) {

    if (history.pushState) {

        history.pushState(null, null, $(obj).attr('href'));
        fillInTable();
        e.preventDefault();
    }

    return true;
}


// This manages the loading spinner for the table
function manageSpinner(present) {

    var spinner = $('div.spinner');
    var spinnerParent = $('div.spinnerParent');

    if (present) {
        // If the spinner isn't there, create it
        if (spinnerParent.length == 0) {
            var spinnerParentHtml = $('<div/>', {'class': 'spinnerParent'});
            var spinnerHtml = $('<div/>', {'class': 'spinner'});
            spinnerHtml.append($('<div/>', {'class': 'bounce1'}));
            spinnerHtml.append($('<div/>', {'class': 'bounce2'}));
            spinnerHtml.append($('<div/>', {'class': 'bounce3'}));
            spinnerParentHtml.append(spinnerHtml);

            $('#dynamicTableDiv').prepend(spinnerParentHtml);
        }
    }
    else {
        // Remove the spinner
        spinner.fadeOut(500, function() { spinnerParent.remove(); });
    }
}


function addStatusMessage(category, message) {

    // Generates a random id for the alert so that the setTimeout function below only applies to that specific alert
    var alertId = Math.floor((Math.random() * 100000) + 1);
    var cssCategory = category == 'success' ? 'alert-success' : 'alert-danger';
    // Create the new alert
    var alert = $('<div />', {'id': 'bottomAlert' + alertId, 'class': 'alert alert-dismissible fade in ' + cssCategory, 'role': 'alert'}).text(message).append(
        $('<button />', {'type': 'button', 'class': 'close', 'data-dismiss': 'alert', 'aria-label': 'Close'}).append(
            $('<span />', {'aria-hidden': 'true'}).text('x')
        )
    );
    // Remove any existing alerts and fade in the new alert
    $('#bottomOuterAlertDiv').hide().empty().append(alert).fadeIn();
    // Fade out the alert after a set amount of time based on its category
    setTimeout(function () {
        $('#bottomAlert' + alertId).fadeOut(function() {$(this).remove()}); },
        (category == 'success' ? 5000 : 8000)
    );
}


function setPagination(currPage, numPages, api) {

    if (currPage && numPages && api) {
        var paginationDiv = $('#pagination');

        for (var i = 1; i <= numPages; i++) {

            var pageButton = $('#itemPage' + String(i));
            // If the page button does not exist, create it
            if (pageButton.length == 0) {
                var cssClass = currPage == i ? 'active' : '';
                $('<li />', {'id': 'itemPage' + i, 'class': cssClass}).append(
                    $('<a />', {'href': '/' + api + '?' + jQuery.param({'page': i}), 'onclick': 'changePage(this, event)'}).text(i)
                ).appendTo(paginationDiv).hide().fadeIn('fast')
            }
            // If the page button does exist, make sure the correct button is marked as active
            else {
                currPage == i ? pageButton.addClass('active') : pageButton.removeClass('active');
            }
        }

        var i = numPages + 1;
        // If there are some pagination buttons remaining after looping through the API results, remove them
        var numTotalPaginationButtons = $('#pagination li').size();
        while (i <= numTotalPaginationButtons) {

            if ($('#itemPage' + String(i)).length != 0) {
                $('#itemPage' + String(i)).fadeOut('fast', function () { $(this).remove(); });
            }
            i++;
        }

        // Fade in the pagination on first load
        if (paginationDiv.hasClass('hidden')) {
            paginationDiv.removeClass('hidden').hide().fadeIn('fast');
        }
    }
    else {
        throw 'All parameters must be specified in the setPagination function';
    }
}


function insertTableRow(tableRow) {
    tableRow.insertBefore('#addItemRow')
        .find('td').wrapInner('<div style="display: none;" />')
        .parent().find('td > div')
        .slideDown('fast', function () {
            var $set = $(this);
            $set.replaceWith($set.contents());
        });
}


function appendTableRow(tableRow) {
    tableRow.appendTo('#dynamicTable tbody')
        .find('td').wrapInner('<div style="display: none;" />')
        .parent().find('td > div')
        .slideDown('fast', function () {
            var $set = $(this);
            $set.replaceWith($set.contents());
        });
}


function removeEmptyTableRows(startRow) {

    var numTotalRows = $('#dynamicTable tr').size();
    while (startRow < numTotalRows) {

        var tableRow = $('#dynamicTableRow' + String(startRow));

        if (tableRow.length != 0) {
            tableRow.find('td')
                .wrapInner('<div style="display: block;" />')
                .parent()
                .find('td > div')
                .slideUp('fast', function () { $(this).parent().parent().remove(); });
        }

        startRow++;
    }
}


function redirectToLastPage(api) {

    $.getJSON(('/api/v1/' + api), function (result) {

        var url = ('/' + api + '?page=' + String(result['meta']['pages']));

        if (history.pushState) {

            history.pushState(null, null, url);
            fillInTable();
        }
        else {
            window.location.href = url;
        }
    });
}

function getApiUrl(api) {
    var urlVars = getUrlVars() || {};
    var filter = $('#filterRow input').val();
    if (filter) {
        urlVars['search'] = filter;
    }

    return ('/api/v1/' + api + '?' + jQuery.param(urlVars));
}
