/* ==========================================
   SPEECH RECOGNITION
========================================== */

const recognition = new webkitSpeechRecognition();

recognition.continuous = false;
recognition.lang = "en-US";

recognition.onresult = function(event){

    const text = event.results[0][0].transcript;

    document.getElementById("messageInput").value = text;

    document
        .getElementById("voiceStatus")
        .classList.add("d-none");

};

recognition.onend = function(){

    document
        .getElementById("voiceStatus")
        .classList.add("d-none");

};

recognition.onerror = function(){

    document
        .getElementById("voiceStatus")
        .classList.add("d-none");

};

/* ==========================================
   START VOICE
========================================== */

function startVoice(){

    document
        .getElementById("voiceStatus")
        .classList.remove("d-none");

    recognition.start();

}

/* ==========================================
   SPEAK RESPONSE
========================================== */

function speakResponse(){

    const responses =
        document.querySelectorAll(".ai-response");

    if(responses.length === 0)
        return;

    const latest =
        responses[responses.length - 1];

    let text =
        latest.innerText;

    /* Remove emojis */

    text = text.replace(
        /[\p{Emoji_Presentation}\p{Extended_Pictographic}]/gu,
        ""
    );

    /* Remove markdown */

    text = text.replace(
        /[*_`>#]/g,
        ""
    );

    /* Remove extra blank lines */

    text = text.replace(
        /\n{2,}/g,
        "\n"
    );

    const utterance =
        new SpeechSynthesisUtterance(text);

    utterance.rate = 1;
    utterance.pitch = 1;
    utterance.volume = 1;

    speechSynthesis.cancel();
    speechSynthesis.speak(utterance);

}

/* ==========================================
   CHAT AUTO SCROLL
========================================== */

const chatBox =
    document.getElementById("chatBox");

if(chatBox){

    chatBox.scrollTop =
        chatBox.scrollHeight;

}

/* ==========================================
   FORM SUBMIT
========================================== */

const form =
    document.getElementById("chatForm");

const sendBtn =
    document.getElementById("sendBtn");

const typing =
    document.getElementById("typing");

if(form){

    form.addEventListener(
        "submit",
        function(){

            typing.style.display =
                "block";

            sendBtn.disabled =
                true;
            sendBtn.innerHTML =
                '<div class="spinner-border spinner-border-sm"></div>';

        }
    );

}

/* ==========================================
   ENTER KEY
========================================== */

const input =
    document.getElementById("messageInput");

if(input){

    input.addEventListener(
        "keydown",
        function(event){

            if(
                event.key === "Enter"
                &&
                !event.shiftKey
            ){

                event.preventDefault();

                form.submit();

            }

        }
    );

}

/* ==========================================
   WINDOW LOAD
========================================== */

window.onload = function(){

    if(chatBox){

        chatBox.scrollTop =
            chatBox.scrollHeight;

    }

    const messages =
    document.querySelectorAll(".message");

    if(messages.length > 0){

        const welcome =
        document.getElementById("welcomeSection");

        if(welcome){

            welcome.style.display =
            "none";

        }

    }

};
function copyResponse(button){

    const message =
        button
        .closest(".bot-message")
        .querySelector("pre")
        .innerText;

    navigator.clipboard.writeText(message);

    button.innerHTML =
        '<i class="bi bi-check-lg"></i>';

    button.classList.add("active");    

    setTimeout(function(){

        button.innerHTML =
            '<i class="bi bi-copy"></i>';

        button.classList.remove("active");

    },1500);

}
document
.querySelectorAll(".prompt-chip")
.forEach(function(chip){

    chip.addEventListener(

        "click",

        function(){

            document
            .getElementById("messageInput")
            .value =
            this.innerText;

            document
            .getElementById("messageInput")
            .focus();

        }

    );

});

/*==========================================
Dynamic Greeting
==========================================*/

const greeting =
document.getElementById("greetingText");

if(greeting){

    const hour =
    new Date().getHours();

    if(hour < 12){

        greeting.innerHTML =
        "🌅 Good Morning";

    }

    else if(hour < 17){

        greeting.innerHTML =
        "☀️ Good Afternoon";

    }

    else{

        greeting.innerHTML =
        "🌙 Good Evening";

    }

}
/*==========================================
LIKE MESSAGE
==========================================*/

function likeMessage(button){

    button.classList.toggle("active");

}

/*==========================================
DISLIKE MESSAGE
==========================================*/

function dislikeMessage(button){

    button.classList.toggle("active");

}
/*==========================================
CHAT HISTORY
==========================================*/

document
.querySelectorAll(".history-item")
.forEach(function(item){

    item.addEventListener(

        "click",

        function(){

            document
            .querySelectorAll(".history-item")
            .forEach(function(i){

                i.classList.remove("active");

            });

            this.classList.add("active");

        }

    );

});
/*==========================================
CREATE TICKET
==========================================*/

function createTicket(){

    document.getElementById("messageInput").value = "yes";

    document.getElementById("chatForm").submit();

}

/*==========================================
CONTINUE CHAT
==========================================*/

function continueChat(){

    document.getElementById("messageInput").focus();

}