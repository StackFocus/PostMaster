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
            addDomainToTable(name);
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
}


function setPagination(numPages, currentPage) {

    for (var i = 1; i <= numPages; i++) {

        $('#domainPagination').hide()
        $('#domainPagination').append('\
            <li' + ((currentPage == i) ? ' class="active"' : '') + '><a href="' + '/domains?page=' + i + '">' + i + '</a></li>\
        ');
    }
}


$(document).ready(function () {

    var domainsUrl = '/api/v1/domains';
    var urlVars = getUrlVars();

    if ('page' in urlVars) {
        domainsUrl += '?page=' + urlVars['page'];
    }

    $.getJSON(domainsUrl, function (result) {

        $.each(result['items'], function (i, domain) {
            addDomainToTable(domain.name);
        });

        setPagination(result['meta']['pages'], result['meta']['page']);

        $('#domainTable').removeClass('hidden').hide().fadeIn('fast');
        $('#domainPagination').fadeIn('fast')
    });


    // This has the enter key when in the #newDomainInput trigger a click on the Add button
    $('#newDomainInput').keyup(function (e) {
        var key = e.which;
        if (key == 13) {
            $('#newDomainAnchor').trigger('click');
            return false;
        }
    });


    $('#newDomainAnchor').on('click', function () {
        $('#statusMessage div.alert button').trigger('click');
        newDomain($('#newDomainInput').val());
        e.preventDefault();
    });
});
