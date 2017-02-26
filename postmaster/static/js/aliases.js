// Creates a new alias via the API

function newAlias(source, destination) {

    $.ajax({
        url: '/api/v1/aliases',
        type: 'post',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            'source': source,
            'destination': destination
        }),

        success: function (response) {
            addStatusMessage('success', 'The alias was added successfully');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });
}


// Deletes an alias via the API
function deleteAlias (id) {

    $.ajax({
        url: '/api/v1/aliases/' + id,
        type: 'delete',

        success: function (data) {
            addStatusMessage('success', 'The alias was successfully removed');
            fillInTable();
        },

        error: function (response) {
            addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
        }
    });
}


// Sets the event listeners for x-editable
function editableAliasEventListeners() {

    var sourceAlias = $('a.sourceAlias');
    var destinationAlias = $('a.destinationAlias');

    sourceAlias.unbind();
    sourceAlias.tooltip();

    destinationAlias.unbind();
    destinationAlias.tooltip();

    sourceAlias.editable({
        params: function (params) {
            return JSON.stringify({'source': params.value})
        },

        success: function () {
            addStatusMessage('success', 'The source alias was changed successfully');
        }
    });

    destinationAlias.editable({
        params: function (params) {
            return JSON.stringify({ 'destination': params.value })
        },

        success: function () {
            addStatusMessage('success', 'The destination alias was changed successfully');
        }
    });
}

// Sets the event listeners in the dynamic table
function aliasEventListeners() {

    var sourceAlias = $('a.sourceAlias');
    var destinationAlias = $('a.destinationAlias');
    var newItemAnchor = $('#newItemAnchor');

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

    $('#dynamicTable').on('click', 'a.deleteAnchor', function (e) {
        deleteAlias($(this).attr('data-pk'));
        e.preventDefault();
    });

    // When the Add button is clicked, it will POST to the API
    newItemAnchor.on('click', function (e) {

        // Close any status messages
        $('#statusMessage div.alert button').trigger('click');

        var aliasSourceInput = $('#newAliasSourceInput');
        var aliasDestinationInput = $('#newAliasDestinationInput');

        // If aliasSourceInput is empty, highlight it in red
        if (!aliasSourceInput.val()) {
            aliasSourceInput.parent().addClass('has-error');
            aliasSourceInput.focus();
        }
            // If aliasDestinationInput is empty, highlight it in red
        else if (!aliasDestinationInput.val()) {
            aliasDestinationInput.parent().addClass('has-error');
            aliasDestinationInput.focus();
        }
        else {
            // Remove any error bordering on the input fields
            aliasSourceInput.parent().removeClass('has-error');
            aliasDestinationInput.parent().removeClass('has-error');
            // Create the new user
            newAlias(aliasSourceInput.val(), aliasDestinationInput.val());
            aliasSourceInput.val('');
            aliasDestinationInput.val('');
            $('#filterRow input').val('');
        }

        e.preventDefault();
    });

    var newAliasInputs = $('#newAliasSourceInput, #newAliasDestinationInput');
    newAliasInputs.unbind();
    // When the user clicks out of the errored input field, the red border disappears
    newAliasInputs.blur(function () {
        $('#newAliasSourceInput').parent().removeClass('has-error');
        $('#newAliasDestinationInput').parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    newAliasInputs.keyup(function (e) {
        var key = e.which;
        if (key == 13) {
            $('#newItemAnchor').trigger('click');
        }
    });
}


// Loads the dynamic table and pagination
function fillInTable () {
    // Set the loading spinner
    manageSpinner(true);

    // If the page or filter was specified, get the appropriate API URL
    apiURL = getApiUrl('aliases');

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            // Query the existing table row
            var tableRow = $('#dynamicTableRow' + String(i));
            // Create a new table row to be inserted or replace the current one
            var newTableRow = $('<tr />', {'id': 'dynamicTableRow' + String(i)});
            var columnDataUrl = '/api/v1/aliases/' + item.id;
            var source_td = $('<td />', {'data-title': 'Source: '}).append(
                $('<a />', {'href': '#', 'class': 'sourceAlias', 'data-pk': item.id, 'data-url': columnDataUrl,
                            'title': 'Click to change the source of the alias'}).text(item.source)
            );
            var destination_td = $('<td />', {'data-title': 'Destination: '}).append(
                $('<a />', {'href': '#', 'class': 'destinationAlias', 'data-pk': item.id, 'data-url': columnDataUrl,
                            'title': 'Click to change the destination of the alias'}).text(item.destination)
            );
            var delete_td = $('<td />', {'data-title': 'Action: '}).append(
                $('<a />', {'href': '#', 'class': 'deleteAnchor', 'data-pk': item.id}).text('Delete')
            );
            // Add the new columns to the new table row
            newTableRow.append(source_td).append(destination_td).append(delete_td);

            // If the table row exists, then replace it, otherwise insert it
            if (tableRow.length > 0) {
                tableRow.replaceWith(newTableRow);
            }
            else {
                insertTableRow(newTableRow);
            }

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages'];
        setPagination(result['meta']['page'], pages, 'aliases');
        //Activate x-editable on new elements and other events
        editableAliasEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {
        // Remove the loading spinner
        manageSpinner(false);
        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('aliases');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Sets the default event listeners
    aliasEventListeners();

    // Set the defaults for x-editable
    $.fn.editable.defaults.mode = 'inline';
    $.fn.editable.defaults.anim = 100;
    $.fn.editable.defaults.type = 'text';
    $.fn.editable.defaults.ajaxOptions = {
        type: 'PUT',
        dataType: 'JSON',
        contentType: 'application/json'
    };
    $.fn.editable.defaults.params = function (params) {
        return JSON.stringify({ 'value': params.value })
    };
    $.fn.editable.defaults.error = function (response) {
        addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
    };
    $.fn.editable.defaults.display = function (value) {
        $(this).html(filterText(value.toLowerCase()));
    };

    // Populate the table
    fillInTable();
});
