// ── Voice Input via Web Speech API ───────────────────────────────────────────
const voiceBtn = document.getElementById('voice-btn');

if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
  // Browser does not support
  if (voiceBtn) {
    voiceBtn.title = 'Voice input not supported in this browser';
    voiceBtn.style.opacity = '0.4';
    voiceBtn.disabled = true;
  }
} else {
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const recognition = new SpeechRecognition();

  recognition.continuous      = false;
  recognition.interimResults  = true;
  recognition.maxAlternatives = 1;
  // Support Hindi + Marathi + English
  recognition.lang = 'hi-IN'; // Change to 'mr-IN' for Marathi, 'en-IN' for English

  let isListening = false;

  voiceBtn.addEventListener('click', () => {
    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  });

  recognition.onstart = () => {
    isListening = true;
    voiceBtn.classList.add('listening');
    voiceBtn.title = 'Listening... Click to stop';
    voiceBtn.textContent = '🔴';
  };

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    const chatInput  = document.getElementById('chat-input');
    if (chatInput) {
      chatInput.value = transcript;
      if (typeof autoResize === 'function') autoResize(chatInput);
    }
  };

  recognition.onend = () => {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceBtn.title = 'Voice Input';
    voiceBtn.textContent = '🎤';
  };

  recognition.onerror = (event) => {
    isListening = false;
    voiceBtn.classList.remove('listening');
    voiceBtn.textContent = '🎤';
    if (event.error !== 'no-speech') {
      console.warn('Speech recognition error:', event.error);
    }
  };
}
