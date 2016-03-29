// Read a page's GET URL variables and return them as an associative array.
// Inspired from http://www.drupalden.co.uk/get-values-from-url-query-string-jquery
function getUrlVars() {
    var vars = [], hash;
    if (window.location.href.indexOf('?') != -1) {
        var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');

        for (var i = 0; i < hashes.length; i++) {
            hash = hashes[i].split('=');
            vars.push(hash[0]);
            vars[hash[0]] = hash[1];
        }
    }

    return vars;
}


// Inspired from https://github.com/janl/mustache.js/blob/master/mustache.js
function filterText(text) {
     var entityMap = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#39;',
        '/': '&#x2F;',
        '`': '&#x60;',
        '=': '&#x3D;'
    };

    return String(text).replace(/[&<>"'`=\/]/g, function fromEntityMap (s) {
      return entityMap[s];
    });
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

    var spinner = $('div.loader');

    if (present) {
        if (spinner.length == 0) {
            $('#dynamicTableDiv').prepend('<div class="loader"></div>');
        }
    }
    else {
        // Remove the spinner but keep the gray background with opacity
        spinner.css('background', 'rgba(255, 255, 255, 0.7)');
        // Remove the gray background with opacity after 300 ms
        setTimeout(function () {
            spinner.fadeOut('fast', function() { spinner.remove() });
        }, 400);
    }
}


function addStatusMessage(category, message) {

    // Generates a random id for the alert so that the setTimeout function below only applies to that specific alert
    var alertId = Math.floor((Math.random() * 100000) + 1);

    $('#bottomOuterAlertDiv').html('\
        <div id="bottomAlert' + alertId + '" class="alert ' + ((category == 'success') ? 'alert-success' : 'alert-danger') + ' alert-dismissible fade in" role="alert">\
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                ' + message + '\
        </div>\
    ').hide().fadeIn();

    setTimeout(function () {
        $('#bottomAlert' + alertId).fadeOut(function() {$(this).remove()}); },
        ((category == 'success') ? 5000 : 8000)
    );
}


function setPagination(currPage, numPages, api) {

    if (currPage && numPages && api) {
        var paginationDiv = $('#pagination');

        for (var i = 1; i <= numPages; i++) {

            var pageButton = $('#itemPage' + String(i));
            // If the page button does not exist, create it
            if (pageButton.length == 0) {
                $('<li' + ((currPage == i) ? ' class="active"' : '') + ' id="' + ('itemPage' + String(i)) + '">\
                    <a href="' + '/' + api + '?page=' + i + '" onclick="changePage(this, event)">' + i + '</a></li>').appendTo(paginationDiv).hide().fadeIn('fast');
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
    $(tableRow).insertBefore('#addItemRow')
        .find('td').wrapInner('<div style="display: none;" />')
        .parent().find('td > div')
        .slideDown('fast', function () {
            var $set = $(this);
            $set.replaceWith($set.contents());
        });
}


function appendTableRow(tableRow) {
    $(tableRow).appendTo('#dynamicTable tbody')
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
    var urlVars = getUrlVars();
    var filter = $('#filterRow input').val();

    if ('page' in urlVars && filter != '') {
        return ('/api/v1/' + api + '?page=' + urlVars['page'] + '&search=' + filter);
    }
    else if ('page' in urlVars) {
        return ('/api/v1/' + api + '?page=' + urlVars['page']);
    }
    else if (filter != '') {
        return ('/api/v1/' + api + '?&search=' + filter);
    }
    else {
        return ('/api/v1/' + api);
    }
}
