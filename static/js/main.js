function updateLocalUsersData() {
    // $.get('/find_local_users', {}, function(data) {
    // console.log(data); // ответ от сервера
    // });
    $.ajax({
    type: 'GET',
    url: '/find_local_users',
    data: {},
    dataType: 'json',
    success: function(data) {
        data.forEach(function(item, i, arr) {
          alert( i + ": " + item + " (массив:" + arr + ")" );
        });
        }, // обработка ответа от сервера
    error: function(jqXHR) { console.log('Ошибка выполнения'); },
    complete: function() { console.log('Завершение выполнения'); }
});
}

