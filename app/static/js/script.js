$(document).ready(function() {
    $('.select2').select2({
        tags: true, // Habilitar a adição de tags personalizadas
        tokenSeparators: [',', ' '], // Separadores de tags
        placeholder: 'Digite um município ou selecione uma opção'
    });
});