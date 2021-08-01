function leaveRoom(e, user_id, room_id){
    console.log(user_id, room_id)
    e.preventDefault()
    var socket = io.connect('http://127.0.0.1:5000');
    console.log(user_id, room_id)
    let data_ = {
        user_id,
        room_id
    }


    var xhr = new XMLHttpRequest()
    var method = 'POST'
    var url = `http://127.0.0.1:5000/leave-room`
    xhr.responseType = 'json'
    xhr.open(method, url)
    xhr.setRequestHeader("HTTP_X_REQUESTED_WITH","XMLHttpRequest")
    xhr.setRequestHeader("X-Requested-With","XMLHttpRequest")
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function(){
      const status = xhr.status
      const server_response = xhr.response
      console.log(server_response, status)
      window.location = '/main'
        
    }

    const data = {
        user_id,
        room_id
    }

    xhr.send(JSON.stringify(data))
    

}