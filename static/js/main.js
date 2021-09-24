function updateLocalUsersData() {
    // $.get('/find_local_users', {}, function(data) {
    // console.log(data); // ответ от сервера
    // });
    $.ajax({
    type: 'GET',
    url: '/find_local_users',
    data: {},
    dataType: 'text',
    success: function(data) { document.getElementById("221").innerText = data; }, // обработка ответа от сервера
    error: function(jqXHR) { console.log('Ошибка выполнения'); },
    complete: function() { console.log('Завершение выполнения'); }
});
}

