jQuery(document).ready(function ($) {
    $('#id_text').focus();
    $('#id_text').on('keypress', function () {
        $('.has-error').hide();
    });
});
