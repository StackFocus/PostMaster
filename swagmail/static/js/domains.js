function addDomainToTable(name) {

    $('#newDomainRow').before('\
        <tr>\
            <td>' + name + '</td>\
            <td><a href="#" class="deleteDomain">Delete</a></td>\
        </tr>\
    ');
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


$(document).ready(function () {

    $.getJSON('/api/v1/domains', function (result) {
        $.each(result['items'], function (i, domain) {
            addDomainToTable(domain.name);
        });
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
