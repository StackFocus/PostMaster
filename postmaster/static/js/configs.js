// Sets the event listeners in the dynamic table
function configEventListeners () {

    var configBoolItems = $('a.configBool');
    var configTextItems = $('a.configText');
    var tooltipAnchors = $("#dynamicTable tr td a[title]");
    tooltipAnchors.unbind();
    tooltipAnchors.tooltip();

    configBoolItems.unbind();
    configBoolItems.editable({
        type: 'select',
        mode: 'inline',
        showbuttons: false,
        anim: 100,
        source: [
              {value: 'True', text: 'True'},
              {value: 'False', text: 'False'}
        ],

        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({'value': params.value})
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The setting was changed successfully');
        }
    });

    configTextItems.unbind();
    configTextItems.editable({
        type: 'text',
        mode: 'inline',
        anim: 100,
        ajaxOptions: {
            type: 'PUT',
            dataType: 'JSON',
            contentType: 'application/json'
        },

        params: function (params) {
            return JSON.stringify({ 'value': params.value })
        },

        error: function (response) {
            // The jQuery('div />') is a work around to encode all html characters
            addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
        },

        success: function () {
            addStatusMessage('success', 'The setting was changed successfully');
        }
    });
}


// Loads the dynamic table and pagination
function fillInTable () {
    // Set the loading spinner
    manageSpinner(true);

    // If the page was specified in the URL, then add it to the API url
    var urlVars = getUrlVars();
    'page' in urlVars ? apiURL = '/api/v1/configs?page=' + urlVars['page'] : apiURL = '/api/v1/configs';

    // Query the API
    $.getJSON(apiURL, function (result) {

        var i = 1;
        // For each item, add a row, but if the row exists, just change the value
        $.each(result['items'], function (j, item) {
            var tableRow = $('#dynamicTableRow' + String(i));
            var html = '';
            var cssClass = item.value == 'True' || item.value == 'False' ? 'configBool' : 'configText';

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-title="Setting: ">' + item.setting + '</td>\
                    <td data-title="Value: "><a href="#" class="' + cssClass + '" data-pk="' + item.id + '" data-url="/api/v1/configs/' + item.id + '" title="Click to change the setting value">' + item.value + '</a></td>';
            tableRow.length == 0 ? html += '</tr>' : null;
            tableRow.length == 0 ? appendTableRow(html) : tableRow.html(html);

            i++;
        });

        // Clean up the table
        removeEmptyTableRows(i);
        // Set the pagination
        result['meta']['pages'] == 0 ? pages = 1 : pages = result['meta']['pages'];
        setPagination(result['meta']['page'], pages, 'configs');
        //Activate x-editable on new elements and other events
        configEventListeners();
        // Remove the loading spinner
        manageSpinner(false);
    })
    .fail(function (jqxhr, textStatus, error) {

        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('configs');
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
});
