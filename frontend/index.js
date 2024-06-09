const msgerForm = get(".msger-inputarea");
const msgerInput = get(".msger-input");
const msgerChat = get(".msger-chat");
const inputField=document.getElementById('input_field');
const sendButton=document.getElementById('send_button');

const BOT_MSGS = [
  "Hi, how are you?",
  "Ohh... I can't understand what you trying to say. Sorry!",
  "I like to play games... But I don't know how to play!",
  "Sorry if my answers are not relevant. :))",
  "I feel sleepy! :("
];

// Icons made by Freepik from www.flaticon.com
const BOT_IMG = "https://cdn-icons-png.flaticon.com/512/4711/4711987.png";
const PERSON_IMG = "https://cdn-icons-png.flaticon.com/512/1144/1144760.png";
const BOT_NAME = "BOT";
const PERSON_NAME = "Sajad";

const UUIDGeneratorBrowser = () =>
  // Generate a UUID using a random number generator provided by the browser's crypto API
  ([1e7] + -1e3 + -4e3 + -8e3 + -1e11).replace(/[018]/g, c =>
    // For each character 'c' in the UUID template, replace it with a randomly generated hexadecimal digit
    (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
  );

async function buttonclick(message_id,user_message) {
        inputField.disabled=true;
        sendButton.disabled=true;
        fetch("http://127.0.0.1:8000/api/askpatentgpt", {
                method: "POST",
                 headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    query: user_message
                })
            })
                .then(response => {
                    console.log(response)
                    console.log(response.body)
                    const reader = response.body.getReader();
                    const decoder = new TextDecoder("utf-8");
                    

                    function readStream() {
                        reader.read().then(({ done, value }) => {
                            if (done) {
                                console.log("Stream complete");
                                inputField.disabled=false;
                                sendButton.disabled=false;
                                return;
                            }

                            const chunk = decoder.decode(value, { stream: true });
                            console.log('chunk',chunk)
                            let message_element=document.getElementById(message_id);
                            if (message_element) {
                                let word = "";
                                for (let char of chunk) {
                                    if (char === " " || char === "\n") {
                                        message_element.innerHTML += word + char;
                                        word = "";
                                    } else {
                                        word += char;
                                    }
                                }
                                message_element.innerHTML += word; // Add any remaining characters in the word
                            }
                            // output.innerHTML += chunk.replace(/data:(\d+)\n\n/g, '$1<br>');

                            readStream();
                        });
                    }

                    readStream();
                })
                .catch(error => console.error("Error fetching the stream:", error));

    }


  

msgerForm.addEventListener("submit", event => {
  event.preventDefault();

  const msgText = msgerInput.value;
  if (!msgText) return;
  let message_id=UUIDGeneratorBrowser()    
  appendMessage(PERSON_NAME, PERSON_IMG, "right", msgText,message_id);
  msgerInput.value = "";

  botResponse(msgText);
});

function appendMessage(name, img, side, text,message_id) {
  //   Simple solution for small apps
  const msgHTML = `
    <div class="msg ${side}-msg">
      <div class="msg-img" style="background-image: url(${img})"></div>

      <div class="msg-bubble">
        <div class="msg-info">
          <div class="msg-info-name">${name}</div>
          <div class="msg-info-time">${formatDate(new Date())}</div>
        </div>

        <div class="msg-text" id="${message_id}">${text}</div>
      </div>
    </div>
  `;

  msgerChat.insertAdjacentHTML("beforeend", msgHTML);
  msgerChat.scrollTop += 500;
}

function botResponse(user_message) {
    let message_id=UUIDGeneratorBrowser();
    let msgText=""
    appendMessage(BOT_NAME, BOT_IMG, "left", msgText,message_id);
   buttonclick(message_id,user_message);
}

// Utils
function get(selector, root = document) {
  return root.querySelector(selector);
}

function formatDate(date) {
  const h = "0" + date.getHours();
  const m = "0" + date.getMinutes();

  return `${h.slice(-2)}:${m.slice(-2)}`;
}

function random(min, max) {
  return Math.floor(Math.random() * (max - min) + min);
}
