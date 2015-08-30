function pullDownLoginPanel() {
    var bodyHeight = $('#body').height();
    var navHeight = $('#navigation-bar').height();
    var loginRowHeight = $('#loginRow').height();
    $('#loginRow').css('margin-top', (bodyHeight - navHeight - loginRowHeight) / 3);
}

$(document).ready(function () {
    pullDownLoginPanel();
});

$(window).resize(function () {
    pullDownLoginPanel();
});
