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


function addStatusMessage(category, message) {

    $('#statusMessage').html('\
        <div class="alert ' + ((category == 'success') ? 'alert-success' : 'alert-danger') + ' alert-dismissible loginAlert fade in" role="alert">\
                <button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                ' + message + '\
        </div>\
    ').hide().fadeIn('fast');
}


function newDomain(name) {

    $.ajax({
        url: '/api/v1/domains',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({'name': name}),

        success: function (data) {
            addStatusMessage('success', 'The domain was added successfully.');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


function deleteDomain(name) {

    $.ajax({
        url: '/api/v1/domains',
        type: 'delete',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({ 'name': name }),

        success: function (data) {
            addStatusMessage('success', 'The domain was successfully removed.');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


function deleteDomainClick(e) {

    deleteDomain($(e).closest('tr').find('td.domainName').text());
}


function fillInTable() {
    var domainsUrl = '/api/v1/domains';
    var urlVars = getUrlVars();

    // Set the loading spinner
    if ($('div.loader').length == 0) {
        $('#dynamicTable').prepend('<div class="loader"></div>');
    }

    // If the page was specified in the URL, then add it to the API url
    if ('page' in urlVars) {
        domainsUrl += '?page=' + urlVars['page'];
    }

    // Query the API
    $.getJSON(domainsUrl, function (result) {

        var i = 1
        // For each domain, add/change the value in the table
        $.each(result['items'], function (j, domain) {

            var tableRow = $('#domainRow' + String(i));

            // If the row exists, then change it
            if (tableRow.length != 0) {
                tableRow.html('\
                    <td class="domainName">' + domain.name + '</td>\
                    <td><a href="#" class="deleteDomain" onclick="deleteDomainClick(this)">Delete</a></td>\
                ');
            }
            // If the row doesn't exist, then add it
            else {
                $('#newDomainRow').before('\
                    <tr id="domainRow' + String(i) + '">\
                        <td class="domainName">' + domain.name + '</td>\
                        <td><a href="#" class="deleteDomain" onclick="deleteDomainClick(this)">Delete</a></td>\
                    </tr>\
                ');
            }

            i++;
        });

        // If there are some rows remaining after looping through the API results, remove them
        var numTotalRows = $('#domainTable tr').size();
        while (i < numTotalRows) {

            if ($('#domainRow' + String(i)).length != 0) {
                $('#domainRow' + String(i)).remove();
            }
            i++;
        }

        var numPages = result['meta']['pages'];
        var currPage = result['meta']['page'];

        // Set the pagination
        for (var i = 1; i <= numPages; i++) {

            if ($('#domainPage' + String(i)).length == 0) {
                $('#domainPagination').append('\
                    <li' + ((currPage == i) ? ' class="active"' : '') + ' id="' + ('domainPage' + String(i)) + '"><a href="' + '/domains?page=' + i + '">' + i + '</a></li>\
                ');
            }
        }

        var i = numPages + 1;
        // If there are some pagination buttons remaining after looping through the API results, remove them
        var numTotalPaginationButtons = $('#domainPagination li').size();
        while (i <= numTotalPaginationButtons) {

            if ($('#domainPage' + String(i)).length != 0) {
                $('#domainPage' + String(i)).remove();
            }
            i++;
        }

        // Fade in the pagination on first load
        if ($('#domainPagination').hasClass('hidden')) {
            $('#domainPagination').removeClass('hidden').hide().fadeIn('fast');
        }

        setTimeout(function () {
            $('div.loader').remove();
        }, 500);
    })
    .fail(function (jqxhr, textStatus, error) {
        
        // If the resource is not found, then redirect to the first domains page
        if (error == 'NOT FOUND') {
            window.location.href = '/domains';
        }
    });
}


$(document).ready(function () {

    fillInTable();

    // When the Add button is clicked, it will POST to the API
    $('#newDomainAnchor').on('click', function () {

        $('#statusMessage div.alert button').trigger('click');
        newDomain($('#newDomainInput').val());
        $('#newDomainInput').val('');
    });

    // This has the enter key when in the #newDomainInput trigger a click on the Add button
    $('#newDomainInput').keyup(function (e) {

        var key = e.which;
        if (key == 13) {
            $('#newDomainAnchor').trigger('click');
            return false;
        }
    });
});
