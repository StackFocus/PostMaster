// Sets the event listeners in the dynamic table
function configEventListeners () {
    var configBoolItems = $('a.configBool');
    var configTextItems = $('a.configText');
    var configLdapAuth = $('a.configLdapAuth');

    configBoolItems.unbind();
    configBoolItems.tooltip();
    configBoolItems.editable({
        type: 'select',
        showbuttons: false,
        source: [
              {value: 'True', text: 'True'},
              {value: 'False', text: 'False'}
        ]
    });

    configTextItems.unbind();
    configTextItems.tooltip();
    configTextItems.editable({
        display: function (value) {
            $(this).text(value);
        }
    });

    configLdapAuth.unbind();
    configLdapAuth.tooltip();
    configLdapAuth.editable({
        type: 'select',
        showbuttons: false,
        source: [
              {value: 'NTLM', text: 'NTLM'},
              {value: 'SIMPLE', text: 'SIMPLE'}
        ]
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
            // Query the existing table row
            var tableRow = $('#dynamicTableRow' + String(i));
            var boolConfigItems = [
                'Login Auditing',
                'Mail Database Auditing',
                'Enable LDAP Authentication'
            ];

            if($.inArray(item.setting, boolConfigItems) != -1) {
                var cssClass = 'configBool';
            }
            else if(item.setting == 'LDAP Authentication Method') {
                var cssClass = 'configLdapAuth';
            }
            else {
                var cssClass = 'configText';
            }

            // Create a new table row to be inserted or replace the current one
            var newTableRow = $('<tr />', {'id': 'dynamicTableRow' + String(i)});
            var setting_td = $('<td />', {'data-title': 'Setting: '}).text(item.setting);
            var value_td = $('<td />', {'data-title': 'Value: '}).append(
                $('<a />', {'href': '#', 'class': cssClass, 'data-pk': item.id, 'data-url': '/api/v1/configs/' + item.id,
                            'title': 'Click to change the setting value'}).text(item.value)
            );
            // Add the new columns to the new table row
            newTableRow.append(setting_td).append(value_td);

            // If the table row exists, then replace it, otherwise insert it
            if (tableRow.length > 0) {
                tableRow.replaceWith(newTableRow);
            }
            else {
                appendTableRow(newTableRow);
            }

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
        type: 'PATCH',
        dataType: 'JSON',
        contentType: 'application/json'
    };
    $.fn.editable.defaults.params = function (params) {
        return JSON.stringify({ 'value': params.value })
    };
    $.fn.editable.defaults.error = function (response) {
        addStatusMessage('error', jQuery.parseJSON(response.responseText).message);
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
