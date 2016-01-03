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

        success: function (data) {
            addStatusMessage('success', 'The alias was added successfully');
            fillInTable();
        },

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
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

        error: function (data) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(data.responseText).message).html());
        }
    });
}


// Sets the event listeners in the dynamic table
function aliasEventListeners() {

    var sourceAlias = $('a.sourceAlias');
    var destinationAlias = $('a.destinationAlias');
    var deleteAnchor = $('a.deleteAnchor');
    var newItemAnchor = $('#newItemAnchor');

    sourceAlias.unbind();
    sourceAlias.tooltip();

    destinationAlias.unbind();
    destinationAlias.tooltip();

    sourceAlias.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({'source': params.value})
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The source alias was changed successfully');
        }
    });

    destinationAlias.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'destination': params.value })
        },

        error: function(response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The destination alias was changed successfully');
        }
    });


    deleteAnchor.unbind();
    deleteAnchor.on('click', function (e) {
        deleteAlias($(this).attr('data-pk'));
        e.preventDefault();
    });

    // When the Add button is clicked, it will POST to the API
    newItemAnchor.unbind();
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
        }

        e.preventDefault();
    });

    $('#newAliasSourceInput, #newAliasDestinationInput').unbind();
    // When the user clicks out of the errored input field, the red border disappears
    $('#newAliasSourceInput, #newAliasDestinationInput').blur(function () {
        $('#newAliasSourceInput').parent().removeClass('has-error');
        $('#newAliasDestinationInput').parent().removeClass('has-error');
    });

    // When in the input field, this triggers the newItemAnchor when pressing enter
    $('#newAliasSourceInput, #newAliasDestinationInput').keyup(function (e) {
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

    // If the page was specified in the URL, then add it to the API url
    var urlVars = getUrlVars();
    'page' in urlVars ? apiURL = '/api/v1/aliases?page=' + urlVars['page'] : apiURL = '/api/v1/aliases';

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-title="Source: "><a href="#" class="sourceAlias" data-pk="' + item.id + '" data-url="/api/v1/aliases/' + item.id + '" title="Click to change the source of the alias">' + item.source + '</td>\
                    <td data-title="Destination: "><a href="#" class="destinationAlias" data-pk="' + item.id + '" data-url="/api/v1/aliases/' + item.id + '" title="Click to change the destination of the alias">' + item.destination + '</td>\
                    <td data-title="Action: "><a href="#" class="deleteAnchor" data-pk="' + item.id + '">Delete</a></td>';
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? $('#addItemRow').before(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages']
        setPagination(result['meta']['page'], pages, 'aliases');
        //Activate x-editable on new elements and other events
        aliasEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {

        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('aliases');
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

    aliasEventListeners();
});
