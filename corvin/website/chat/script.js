var chats = null;
var chatOpened = null;

let url = new URL(window.location);
url.protocol = "ws:"; url.pathname = '/chat_ws';
const websocket = new WebSocket(url);

websocket.addEventListener("message", ({ data }) => {
    let firstMsg = chats == null;
    if (firstMsg) { // first msg
        if (data == "b") {
            window.location.replace("/login?ic=ba");
            return;
        } else if (data == "n") {
            window.location.replace("/login?ic=na");
            return;
        }
        chats = [];
    }

    const newMsgs = JSON.parse(data);
    console.log(newMsgs)
    for (let i of newMsgs) {
        let chatDivElem = null;
        for (let j of chats)
            if (j.with == i.with) {
                chatDivElem = j.divElem;
                chats = chats.concat(i);
                break;
            }
        if (chatDivElem == null) { // no chat found
            console.log("Could not find " + i.with);
            chatDivElem = document.createElement("div");
            chatDivElem.setAttribute("class", "chatSelector");
            chatDivElem.appendChild(document.createTextNode(i.with));
            newLastMsg = document.createElement("p");
            newLastMsg.setAttribute("class", "lastMsg");
            newLastMsg.appendChild(document.createTextNode(i.messages[0].data.replace(/\n/g, " ")));
            // .replace(/\n/g, "") collapses the message to one line, removes new lines
            chatDivElem.appendChild(newLastMsg);
            // insert before 1st chat
            userlistElement.insertBefore(chatDivElem, document.getElementsByClassName("chatSelector")[0]);
            chatDivElem.addEventListener("click", openChatInWin);
            i.divElem = chatDivElem;
            chats.unshift(i);
        }

        // if this chat is opened, update the chat window
        if (chatDivElem.className == "chatSelector chatSelected")
            addChatsToChatWin(i.messages);
    }
});

function addChatsToChatWin(chatsToAdd, replace=false) {
    const msgsDiv = document.getElementsByClassName("messages")[0];
    function brP() {
        brPEl = document.createElement("p");
        brPEl.setAttribute("class", "msgBr");
        brPEl.appendChild(document.createElement("br"));
        return brPEl; }
    if (replace)
        msgsDiv.textContent = "";
    for (let j of Array.from(chatsToAdd).reverse()) { // Array.from to create shallow copy since reverse changes the original array
        newMsgP = document.createElement("p");
        newMsgP.setAttribute("class", "chatMsg " + (j.sent? "sentMsg": "rcvdMsg"));
        newMsgP.appendChild(document.createTextNode(j.data));
        msgsDiv.appendChild(newMsgP);
        msgsDiv.appendChild(brP()); // space after every message
    }
}

function openChatInWin({ srcElement }, chatObj=null) {
    if (srcElement.className == "lastMsg")
        srcElement = srcElement.parentElement;
    if (srcElement.className == "chatSelector chatSelected") // already opened
        return;
    if (chatOpened)
        chatOpened.divElem.setAttribute("class", "chatSelector");
    srcElement.setAttribute("class", "chatSelector chatSelected");
    if (!chatObj)
        for (let i of chats)
            if (i.divElem == srcElement) {
                chatObj = i;
                break;
            }
    chatOpened = chatObj;
    addChatsToChatWin(chatObj.messages, true);
    mbx['disabled'] = false;
}

function newChat() {
    const toUsn = window.prompt("To:");
    if (toUsn) { // not empty string or null
        const req = new XMLHttpRequest();
        req.open("GET", "/user_exists?u=" + encodeURIComponent(toUsn));
        req.send();
        req.onreadystatechange = () => {
            if (req.readyState != 4)
                return
            if (!req.responseText) { // account does not exist
                window.alert("User does not exist.");
                return;
            }

            newChat = document.createElement("div");
            newChat.setAttribute("class", "chatSelector");
            newChat.appendChild(document.createTextNode(toUsn));
            newLastMsg = document.createElement("p");
            newLastMsg.setAttribute("class", "lastMsg");
            newChat.appendChild(newLastMsg);
            // insert before 1st chat
            document.getElementsByClassName("userList")[0].insertBefore(newChat, document.getElementsByClassName("chatSelector")[0]);
            newChat.addEventListener("click", openChatInWin);
            const chatObj = { "with": toUsn, "messages": [], "divElem": newChat };
            chats.unshift(chatObj);
            openChatInWin({"srcElement": newChat}, chatObj);
        }
    }
}

const mbx = document.getElementsByClassName("msgBox")[0];
const userlistElement = document.getElementsByClassName("userList")[0]
function send(msgData) {
    const msgStr = mbx.value.trim();
    mbx.value = "";
    if (!msgStr) {
        mbx.placeholder = "Cannot send an empty message.";
        return;
    }  else {
        mbx.placeholder = "Enter message ...";
    }
    websocket.send(JSON.stringify({
        "with": chatOpened.with,
        "msgStr": msgStr
    }));
}
