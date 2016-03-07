// Sets the event listeners in the dynamic table
function configEventListeners () {
    var configBoolItems = $('a.configBool');
    var configTextItems = $('a.configText');
    var configLogFile = $('a.configLogFile');

    configBoolItems.unbind();
    configBoolItems.tooltip();
    configBoolItems.editable({
        type: 'select',
        showbuttons: false,
        source: [
              {value: 'True', text: 'True'},
              {value: 'False', text: 'False'}
        ],
    });

    configTextItems.unbind();
    configTextItems.tooltip();
    configTextItems.editable();

    configLogFile.unbind();
    configLogFile.tooltip();
    configLogFile.editable({
        success: function () {
            // Sets the Mail Database Auditing to True in the UI
            $('td:contains("Mail Database Auditing")').next('td').children('a').text('True');
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
            var boolConfigItems = [
                'Login Auditing',
                'Mail Database Auditing',
                'Enable LDAP Authentication'
            ];

            if (item.setting == 'Log File') {
                var cssClass = 'configLogFile'
            }
            else if($.inArray(item.setting, boolConfigItems) != -1) {
                var cssClass = 'configBool'
            }
            else {
                var cssClass = 'configText'
            }

            tableRow.length == 0 ? html += '<tr id="dynamicTableRow' + String(i) + '">' : null;
            html += '<td data-title="Setting: ">' + item.setting + '</td>\
                    <td data-title="Value: "><a href="#" class="' + cssClass + '" data-pk="' + item.id + '" data-url="/api/v1/configs/' + item.id + '" title="Click to change the setting value">' + (item.value != null ? item.value : '') + '</a></td>';
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
        // Remove the loading spinner
        manageSpinner(false);
        // If the resource is not found, then redirect to the last page
        if (error == 'NOT FOUND') {
            redirectToLastPage('configs');
        }
    });
}


$(document).ready(function () {
    // This stops the browser from caching AJAX (fixes IE)
    $.ajaxSetup({ cache: false });

    // Set the defaults for x-editable
    $.fn.editable.defaults.mode = 'inline';
    $.fn.editable.defaults.emptytext = 'Not set';
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
        // The jQuery('div />') is a work around to encode all html characters
        addStatusMessage('error', jQuery('<div />').text(jQuery.parseJSON(response.responseText).message).html());
    };
    $.fn.editable.defaults.success = function () {
        addStatusMessage('success', 'The setting was changed successfully');
    };

    // Populate the table
    fillInTable();

    // When hitting the back/forward buttons, reload the table
    $(window).bind("popstate", function () {
        fillInTable();
    });
});
