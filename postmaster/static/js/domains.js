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

    var newItemAnchor = $('#newItemAnchor');
    var deleteModal = $('#deleteModal');
    var deleteModalBtn = $('#modalDeleteBtn');
    var newDomainInput = $('#newDomainInput');

    deleteModal.unbind('show.bs.modal');
    deleteModal.on('show.bs.modal', function (e) {
        deleteModalBtn.attr('data-pk', $(e.relatedTarget).data('pk'));
    });

    deleteModalBtn.unbind('click');
    deleteModalBtn.on('click', function (e) {
        deleteModal.modal('hide');
        deleteDomain($(this).attr('data-pk'));
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
            $('#filterRow input').val('');
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
function fillInTable(filter) {
    // Set the loading spinner
    manageSpinner(true);

    // If the page or filter was specified, get the appropriate API URL
    apiURL = getApiUrl('domains');

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-pk="' + item.id + '" data-title="Domain: ">' + item.name + '</td>\
                     <td data-title="Action: "><a href="#" class="deleteAnchor" data-pk="' + item.id + '" data-toggle="modal" data-target="#deleteModal">Delete</a></td>';
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? insertTableRow(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages'];
        setPagination(result['meta']['page'], pages, 'domains');
        // Reactive all event listeners
        domainEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        // Remove the loading spinner
        manageSpinner(false);
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

    // When hitting the back/forward buttons, reload the table
    $(window).bind("popstate", function () {
        fillInTable();
    });

    // Set the filter event listener
    var typeWatchOptions = {
        callback: function () { fillInTable() },
        wait: 750,
        captureLength: 2
    };

    $('#filterRow input').typeWatch(typeWatchOptions);
});
