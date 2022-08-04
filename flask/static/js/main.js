window.onload = Init()
    
function Init(){
    Cookies.remove('quest')
    Cookies.remove('answer')
    d_buts = document.getElementsByClassName('delete_but');
    c_buts = document.getElementsByClassName('change_but');
    for (let i = 0; i < d_buts.length; i++) {
            d_buts[i].addEventListener('click', DeleteCheck);
            c_buts[i].addEventListener('click', (event)=>{
                    ident = event.target.getAttribute('id');
                    CancelModerate(ident);
                    StartModerate(ident);
                    InitSaveCancelButtons(ident);
                });
        }

    document.getElementById('insert_quest_btn').addEventListener('click',InsertAjax)

    var open_inserting = document.getElementById('start_insert_new')
    var close_inserting = document.getElementById('stop_insert_new')

    open_inserting.addEventListener('click', () =>{
        document.getElementsByClassName('container')[0].style.display = 'flex'
        close_inserting.style.display = 'block'
        open_inserting.style.display = 'none'
    })
    close_inserting.addEventListener('click', () =>{
        document.getElementsByClassName('container')[0].style.display = 'none'
        close_inserting.style.display = 'none'
        open_inserting.style.display = 'block'
    })
}

function StartModerate(ident){
    quest = document.getElementsByClassName('q_'+ident)[0];
    answer = document.getElementsByClassName('a_'+ident)[0];

    Cookies.set('quest',quest.innerHTML)
    Cookies.set('answer',answer.innerHTML)

    answer.innerHTML = '<textarea id="save_a">'+answer.innerHTML+'</textarea>'
    quest.innerHTML = '<textarea id="save_q">'+quest.innerHTML+'</textarea>'

    document.getElementsByClassName('delete_'+ident)[0].classList.add('hide_but')
    document.getElementsByClassName('change_'+ident)[0].classList.add('hide_but')

    }

function CancelModerate(ident){
    // Чистим все открытые модерации
    old_save_buts = document.getElementsByClassName('save_but');
    old_cancel_buts = document.getElementsByClassName('cancel_but');
    for (let i = 0; i < old_save_buts.length; i++) {
        old_save_buts[i].classList.add('hide_but');
        old_cancel_buts[i].classList.add('hide_but');
     }

    quests = document.getElementsByClassName('quest');
    answers = document.getElementsByClassName('answer');

    if (Cookies.get('quest') != undefined && Cookies.get('answer') != undefined){
        answer.innerHTML = Cookies.get('answer');
        quest.innerHTML = Cookies.get('quest');

    }
    change_buts = document.getElementsByClassName('change_but');
    delete_buts = document.getElementsByClassName('delete_but');

    for (let i = 0; i < change_buts.length; i++) {
        change_buts[i].classList.remove('hide_but');
        delete_buts[i].classList.remove('hide_but');
     }
    }

function InitSaveCancelButtons(ident){
    save_button = document.getElementsByClassName('save_'+ident)[0]
    save_button.classList.remove('hide_but')
    save_button.addEventListener('click', () => {
        SaveAjax(ident)
    })

    cancel_button = document.getElementsByClassName('cancel_'+ident)[0] 
    cancel_button.classList.remove('hide_but')
    cancel_button.addEventListener('click', CancelModerate)
    }


function DeleteCheck(event){
    ident = event.target.getAttribute('id')
    quest = document.getElementsByClassName('q_'+ident)[0].innerHTML;
    answer = document.getElementsByClassName('a_'+ident)[0].innerHTML;

    document.getElementsByClassName('modal')[0].style.display = 'flex'

    confirm_quest = document.getElementById('confirm_quest')
    confirm_answer = document.getElementById('confirm_answer')

    confirm_quest.innerHTML = 'Вопрос: ' + quest
    confirm_answer.innerHTML = 'Ответ: ' +  answer

    document.getElementById('cancel_confirm').addEventListener('click',()=>{
        document.getElementsByClassName('modal')[0].style.display = 'none'
    })

    confirm_delete = document.getElementById('confirm_delete')
    confirm_delete.setAttribute('data-id', ident);
    confirm_delete.addEventListener('click', DeleteAjax)
    
}


function SaveAjax(ident){
   quest = document.getElementById('save_q')
   answer = document.getElementById('save_a')

   if (quest.value == Cookies.get('quest') && answer.value == Cookies.get('answer')){
       alert('Поля не были изменены, нажмите "Отменить" для отмены исправления, либо измените ответ/вопрос')
       return
   }

   $.ajax({
       type:'POST',
       data: JSON.stringify(
           {
               ident: ident,
               quest: quest.value,
               answer: answer.value,
           }
           ),
       url: "/change/",
       dataType : "json",
       contentType: "application/json; charset=utf-8",
       success: function () {
           document.location.reload();
       },
       error: function (response) {
           alert('Ошибка: '+ response['error'])
       }
   });
}

function DeleteAjax(event){
   ident = event.target.getAttribute('data-id');
   $.ajax({
       type:'POST',
       data: JSON.stringify(
           {
               ident: ident,
           }
           ),
       url: "/delete/",
       dataType : "json",
       contentType: "application/json; charset=utf-8",
       success: function () {
           document.location.reload();
       },
       error: function (response) {
           alert('Ошибка: '+ response['error'])
       }
   });
}

function InsertAjax(){
   $.ajax({
       type:'POST',
       data: JSON.stringify($('#insert_quest').serializeArray()),
       url: "/insert/",
       dataType : "json",
       contentType: "application/json; charset=utf-8",
       success: function () {
           document.location.reload();
       },
       error: function (response) {
           alert('Ошибка: '+ response['error'])
       }
   });
}
