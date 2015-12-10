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


function changePage(obj, e) {

    if (history.pushState) {

        history.pushState(null, null, $(obj).attr('href'));
        fillInTable();
        e.preventDefault();
    }

    return true;
}


function addStatusMessage(category, message) {

    $('#statusMessage').html('\
        <div class="alert ' + ((category == 'success') ? 'alert-success' : 'alert-danger') + ' alert-dismissible loginAlert fade in" role="alert">\
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                ' + message + '\
        </div>\
    ').hide().fadeIn('fast');
}


function newUser(email, password) {

    $.ajax({
        url: '/api/v1/users',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'email': email,
            'password': password
        }),

        success: function (data) {
            addStatusMessage('success', 'The user was added successfully.');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}

function deleteUser(id) {

    $.ajax({
        url: '/api/v1/users/' + id,
        type: 'delete',

        success: function (data) {
            addStatusMessage('success', 'The user was successfully removed.');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


function deleteUserClick(obj, e) {

    deleteUser($(obj).attr('data-pk'));
    e.preventDefault();
}


function fillInTable() {
    var apiURL = '/api/v1/users';
    var urlVars = getUrlVars();

    // Set the loading spinner
    if ($('div.loader').length == 0) {
        $('#dynamicTableDiv').prepend('<div class="loader"></div>');
    }

    // If the page was specified in the URL, then add it to the API url
    if ('page' in urlVars) {
        apiURL += '?page=' + urlVars['page'];
    }

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1
        // For each item, add/change the value in the table
        $.each(result['items'], function (j, item) {

            var tableRow = $('#dynamicTableRow' + String(i));

            // If the row exists, then change it
            if (tableRow.length != 0) {
                tableRow.html('\
                    <td class="userEmail" data-pk="' + item.id + '">' + item.email + '</td>\
                    <td class="userPassword">●●●●●●●●●●●●</td>\
                    <td><a href="#" onclick="deleteUserClick(this, event)" data-pk="' + item.id + '">Delete</a></td>\
                ');
            }
                // If the row doesn't exist, then add it
            else {
                $('#addItemRow').before('\
                    <tr id="dynamicTableRow' + String(i) + '">\
                        <td class="userEmail">' + item.email + '</td>\
                        <td class="userPassword">●●●●●●●●●●●●</td>\
                        <td><a href="#" onclick="deleteUserClick(this, event)" data-pk="' + item.id + '">Delete</a></td>\
                    </tr>\
                ');
            }

            i++;
        });

        // If there are some rows remaining after looping through the API results, remove them
        var numTotalRows = $('#dynamicTable tr').size();
        while (i < numTotalRows) {

            if ($('#dynamicTableRow' + String(i)).length != 0) {
                $('#dynamicTableRow' + String(i)).remove();
            }
            i++;
        }

        var numPages = result['meta']['pages'];
        var currPage = result['meta']['page'];

        // Set the pagination
        for (var i = 1; i <= numPages; i++) {

            var pageButton = $('#itemPage' + String(i));

            if (pageButton.length == 0) {
                $('#pagination').append('\
                    <li' + ((currPage == i) ? ' class="active"' : '') + ' id="' + ('itemPage' + String(i)) + '"><a href="' + '/users?page=' + i + '" onclick="changePage(this, event)">' + i + '</a></li>\
                ');
            }
            else {
                if ((currPage == i) && !(pageButton.hasClass('active'))) {
                    pageButton.addClass('active');
                }
                else if ((currPage != i) && (pageButton.hasClass('active'))) {

                    pageButton.removeClass('active');
                }
            }
        }

        var i = numPages + 1;
        // If there are some pagination buttons remaining after looping through the API results, remove them
        var numTotalPaginationButtons = $('#pagination li').size();
        while (i <= numTotalPaginationButtons) {

            if ($('#itemPage' + String(i)).length != 0) {
                $('#itemPage' + String(i)).remove();
            }
            i++;
        }

        // Fade in the pagination on first load
        if ($('#pagination').hasClass('hidden')) {
            $('#pagination').removeClass('hidden').hide().fadeIn('fast');
        }

        setTimeout(function () {
            $('div.loader').remove();
        }, 500);
    })
    .fail(function (jqxhr, textStatus, error) {

        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {

            $.getJSON('/api/v1/users', function (result) {

                var url = ('/users?page=' + String(result['meta']['pages']));

                if (history.pushState) {

                    history.pushState(null, null, url);
                    fillInTable();
                }
                else {
                    window.location.href = url;
                }
            });
        }
    });
}


$(document).ready(function () {

    // IE was caching the AJAX request and causing the table not to update
    $.ajaxSetup({ cache: false });

    fillInTable();

    $(window).bind("popstate", function () {
        fillInTable();
    });

    // When the Add button is clicked, it will POST to the API
    $('#newItemAnchor').on('click', function () {

        $('#statusMessage div.alert button').trigger('click');
        newUser($('#newUserInput').val(), $('#newPasswordInput').val());
        $('#newUserInput').val('');
        $('#newPasswordInput').val('');
    });

    // This has the enter key when in the add field trigger a click on the Add button
    $('#newUserInput, #newPasswordInput').keyup(function (e) {

        var key = e.which;
        if (key == 13) {
            $('#newItemAnchor').trigger('click');
            return false;
        }
    });
});
