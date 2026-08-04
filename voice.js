const recognition =
new webkitSpeechRecognition();

recognition.continuous = false;

recognition.lang = "en-US";

recognition.onresult = function(event){

    const text =
        event.results[0][0].transcript;

    const box =
        document.getElementById(
            "complaint_text"
        );

    if(box){

        box.value = text;

    }

};

function startVoice(){

    recognition.start();

}

function speakResponse(){

    const response =
        document.getElementById(
            "ai_response"
        );

    if(response){

        const utterance =
            new SpeechSynthesisUtterance(
                response.innerText
            );

        speechSynthesis.speak(
            utterance
        );

    }

}