// Creates a new domain via the API
function newDomain(name) {
    if (name) {
        $.ajax({
            url: '/api/v1/domains',
            type: 'post',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify({ 'name': name }),

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
    else {
        throw 'A name must be specified in the newDomain function';
    }
}


// Deletes a domain via the API
function deleteDomain (id) {
    if (id) {
        $.ajax({
            url: '/api/v1/domains/' + id,
            type: 'delete',
            contentType: 'application/json',

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
    else {
        throw 'An id must be specified in the deleteDomain function';
    }
}


// Sets the event listeners in the dynamic table
function domainEventListeners() {

    var deleteAnchor = $('a.deleteAnchor');
    var newItemAnchor = $('#newItemAnchor');
    var newDomainInput = $('#newDomainInput');

    deleteAnchor.unbind();
    deleteAnchor.on('click', function (e) {
        deleteDomain($(this).attr('data-pk'));
        e.preventDefault();
    });

    // When the Add button is clicked, it will POST to the API
    newItemAnchor.unbind();
    newItemAnchor.on('click', function (e) {

        // Close any status messages
        $('#statusMessage div.alert button').trigger('click');

        var domainInput = $('#newDomainInput');

        // If the domainInput is empty, display a red border around it
        if (!domainInput.val()) {
            domainInput.parent().addClass('has-error');
            domainInput.focus();
        }
        else {
            // Remove any error bordering on the input fields
            newDomainInput.parent().removeClass('has-error');
            // Create the new domain
            newDomain(domainInput.val());
            domainInput.val('');
        }

        e.preventDefault();
    });

    // When the user clicks out of the errored input field, the red border disappears
    newDomainInput.unbind();
    newDomainInput.blur(function () {
        newDomainInput.parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    newDomainInput.keyup(function (e) {

        var key = e.which;
        if (key == 13) {
            newItemAnchor.trigger('click');
        }
    });
}


// Loads the dynamic table and pagination
function fillInTable () {
    // Set the loading spinner
    manageSpinner(true);

    // If the page was specified in the URL, then add it to the API url
    var urlVars = getUrlVars();
    'page' in urlVars ? apiURL = '/api/v1/domains?page=' + urlVars['page'] : apiURL = '/api/v1/domains';

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-pk="' + item.id + '">' + item.name + '</td>\
                     <td><a href="#" class="deleteAnchor" data-pk="' + item.id + '">Delete</a></td>';
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? $('#addItemRow').before(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        setPagination(result['meta']['page'], result['meta']['pages'], 'domains');
        // Reactive all event listeners
        domainEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        
        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('domains');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Populate the table
    fillInTable();

    // Set the event listeners
    domainEventListeners();

    // When hitting the back/forward buttons, reload the table
    $(window).bind("popstate", function () {
        fillInTable();
    });
});
