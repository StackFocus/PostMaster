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


function addDomainToTable(name) {

    $('#newDomainRow').before('\
        <tr>\
            <td class="domainName">' + name + '</td>\
            <td><a href="#" class="deleteDomain" onclick="deleteDomainClick(this)">Delete</a></td>\
        </tr>\
    ');
}


function deleteDomainFromTable(name) {

    $('#domainTable tr td').filter(function () {
        return $(this).text() == name;
    }).parent().remove();
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
            //addDomainToTable(name);
            addStatusMessage('success', 'The domain was added successfully.');
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
            deleteDomainFromTable(name);
            addStatusMessage('success', 'The domain was successfully removed.');
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


function deleteDomainClick(e) {

    deleteDomain($(e).closest('tr').find('td.domainName').text());
    fillInTable();
}


function createEventListeners() {
    // When the table is recreated the listeners must be set again

    // This has the enter key when in the #newDomainInput trigger a click on the Add button
    $('#newDomainInput').keyup(function (e) {

        var key = e.which;
        if (key == 13) {
            $('#newDomainAnchor').trigger('click');
            return false;
        }
    });

    // When the Add button is clicked, it will POST to the API
    $('#newDomainAnchor').on('click', function () {

        $('#statusMessage div.alert button').trigger('click');
        newDomain($('#newDomainInput').val());
        $('#newDomainInput').val('');
        fillInTable();
    });
}


function fillInTable() {
    // Fills in the Domain table with the results from the API
    // and fills in the pagination buttons

    // Hide the table and pagination
    $('#domainTable').addClass('hidden')
    $('#domainPagination').addClass('hidden')

    // Set the table to only have the add domain row
    $('#domainTable tbody').html('\
        <tr id="newDomainRow">\
            <td><input id="newDomainInput" class="form-control" type="text" placeholder="Enter a new domain"/></td>\
            <td style="vertical-align: middle"><a href="#" id="newDomainAnchor">Add</a></td>\
        </tr>\
    ');

    var domainsUrl = '/api/v1/domains';
    var urlVars = getUrlVars();

    // If the page was specified in the URL, then add it to the API url
    if ('page' in urlVars) {
        domainsUrl += '?page=' + urlVars['page'];
    }

    // Query the API
    $.getJSON(domainsUrl, function (result) {

        // For each domain, add it to the table
        $.each(result['items'], function (i, domain) {
            addDomainToTable(domain.name);
        });

        var numPages = result['meta']['pages'];
        var currPage = result['meta']['page'];

        // Clear the pagination
        $('#domainPagination').html('');

        // Set the pagination
        for (var i = 1; i <= numPages; i++) {

            $('#domainPagination').hide()
            $('#domainPagination').append('\
                <li' + ((currPage == i) ? ' class="active"' : '') + '><a href="' + '/domains?page=' + i + '">' + i + '</a></li>\
            ');
        }

        // Fade in the table and pagination
        $('#domainTable').removeClass('hidden').hide().fadeIn('fast');
        $('#domainPagination').removeClass('hidden').hide().fadeIn('fast');
    })
    .fail(function (jqxhr, textStatus, error) {
        
        // If the resource is not found, then redirect to the first domains page
        if (error == 'NOT FOUND') {
            window.location.href = '/domains';
        }
    })
    ;

    createEventListeners();
}


$(document).ready(function () {

    fillInTable();
});
