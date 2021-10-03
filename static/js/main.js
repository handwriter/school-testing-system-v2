let user_data = {};
let tooltip = {};

function onContextMenu(e){
    e.preventDefault();
    // showMenu(e.pageX, e.pageY);
    // document.addEventListener('mousedown', onMouseDown, false);
}

function openFile(f_name) {
    SendRequest("GET","/open_file", "f_name=" + f_name, function() {}, false);
}

function deleteFile(f_name) {
    SendRequest("GET","/delete_file", "f_name=" + f_name, function() {location.reload()}, false);
}

function sendFile(f_name) {
    SendRequest("GET","/send_file", "f_name=" + f_name, function() {}, false);
}

function onMouseMove(e) {
    tooltip.style.left = e.clientX - (tooltip.getBoundingClientRect().width / 2) + 'px';
    tooltip.style.top = e.clientY - tooltip.getBoundingClientRect().height - 10 + 'px';
}

function showTooltip(text) {
    tooltip.classList.remove('inactive');
    tooltip.innerText = text;
}

function hideTooltip() {
    tooltip.classList.add('inactive');
}

function afterPageLoad() {
    tooltip = document.querySelector(".tooltip");
}

document.addEventListener('contextmenu', onContextMenu, false);
document.addEventListener('mousemove', onMouseMove, false);


function LoadUserData() {
    var Handler = function(Request)
    {
        user_data = JSON.parse(Request.responseText);
    };

    SendRequest("GET","/user_data", "", Handler, false);
}

function CreateRequest()
{
    var Request = false;

    if (window.XMLHttpRequest)
    {
        //Gecko-совместимые браузеры, Safari, Konqueror
        Request = new XMLHttpRequest();
    }
    else if (window.ActiveXObject)
    {
        //Internet explorer
        try
        {
             Request = new ActiveXObject("Microsoft.XMLHTTP");
        }
        catch (CatchException)
        {
             Request = new ActiveXObject("Msxml2.XMLHTTP");
        }
    }

    if (!Request)
    {
        alert("Невозможно создать XMLHttpRequest");
    }

    return Request;
}

function SendRequest(r_method, r_path, r_args, r_handler, use_loader)
{
    //Создаём запрос
    var Request = CreateRequest();

    //Проверяем существование запроса еще раз
    if (!Request)
    {
        return;
    }
    if (use_loader) {
        document.getElementById("loader").classList.remove("inactive");
    }
    //Назначаем пользовательский обработчик
    Request.onreadystatechange = function()
    {
        //Если обмен данными завершен
        if (Request.readyState == 4)
        {
            if (use_loader) {
                document.getElementById("loader").classList.add("inactive");
            }
            //Передаем управление обработчику пользователя
            r_handler(Request);
        }
    };

    //Проверяем, если требуется сделать GET-запрос
    if (r_method.toLowerCase() == "get" && r_args.length > 0)
    r_path += "?" + r_args;

    //Инициализируем соединение
    Request.open(r_method, r_path, true);

    if (r_method.toLowerCase() == "post")
    {
        //Если это POST-запрос

        //Устанавливаем заголовок
        Request.setRequestHeader("Content-Type","application/x-www-form-urlencoded; charset=utf-8");
        //Посылаем запрос
        Request.send(r_args);
    }
    else
    {
        //Если это GET-запрос

        //Посылаем нуль-запрос
        Request.send(null);
    }
}

function updateLocalUsersData() {
    var Handler = function(Request)
    {
        var resp = JSON.parse(Request.responseText);
        if (resp["users_data"].length == 0) {
            document.getElementById('usersTable').classList.add("inactive");
            document.getElementById('usersNotFound').classList.remove("inactive");
            return;
        }
        document.getElementById('usersTable').classList.remove("inactive");
        document.getElementById('usersNotFound').classList.add("inactive");
        document.getElementById('usersList').innerHTML = "";
        resp['users_data'].forEach(function(entry) {
            addRow(entry[1]['username'], entry[1]['teacher'], resp['connected_users'], entry[0]);
        });
    };

    SendRequest("GET","/find_local_users", "", Handler, true);
}

// function getTop(el) {
//   return el.offsetTop + (el.offsetParent && getTop(el.offsetParent));
// }
//
// function getLeft(el) {
//   return el.offsetLeft + (el.offsetParent && getTop(el.offsetParent));
// }

function connectToTeacher(addr) {

    SendRequest("GET","/connect_to", "addr="+addr, function() {location.reload()}, true);
}

function disconnectFromTeacher() {

    SendRequest("GET","/disconnect_from", "", function() {location.reload()}, true);
}

function SendFile() {
    let file = document.getElementById('file').files[0];
    const reader = new FileReader();
    reader.onloadend = () => {

    // use a regex to remove data url part
            const base64String = reader.result
                .replace('data:', '')
                .replace(/^.+,/, '');

            // log to console
            // logs wL2dvYWwgbW9yZ...
            SendRequest("GET","/send_file", "data=" + base64String, function() {location.reload()}, true);
            console.log(base64String);
        };
    reader.readAsDataURL(file);

}



function addRow(username, teacher, connected_users, ip)
{
  var tableBody = document.getElementById('usersList');
  var newRow = tableBody.insertRow(tableBody.rows.length);
  var usernameCell = newRow.insertCell(0);
  var teacherCell = newRow.insertCell(1);
  var statusCell = newRow.insertCell(2);
  var usernameText = document.createTextNode(username);
  var scoreText = NaN;
  if (teacher) {
      scoreText = document.createTextNode('Учитель');
  } else {
      scoreText = document.createTextNode('Ученик');
  }
  var userStatus = false;
  if (user_data['teacher']) {
      userStatus = document.createElement('img');
      if (connected_users.indexOf(ip) >= 0) {
          userStatus.setAttribute("src", "/static/img/tick.svg");
      } else {
          userStatus.setAttribute("src", "/static/img/cross.svg");
      }
  }
  else if (teacher) {
      userStatus = document.createElement('a');
      if (ip != user_data['connected_teacher']) {
          if (user_data['connected_teacher'] == '') {
              userStatus.setAttribute("onclick", "connectToTeacher('" + ip + "');");
              userStatus.innerHTML = "<button>Подключиться</button>";
          }
      }
      else {
          userStatus.setAttribute("onclick", "disconnectFromTeacher();");
          userStatus.innerHTML = "<button>Отключиться</button>";
      }
  }

  usernameCell.appendChild(usernameText);
  teacherCell.appendChild(scoreText);
  if (userStatus) {
      statusCell.appendChild(userStatus);
  }
}