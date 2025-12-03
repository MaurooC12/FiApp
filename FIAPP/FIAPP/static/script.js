// Smooth scroll behavior
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      target.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Form validation - STRICT: bloquea envío si campos están vacíos
// Feature toggle to enable custom form validation. Default disabled to avoid
// interfering with login/register flows. Set `window.FIAPP_ENABLE_CUSTOM_VALIDATION = true`
// in the console if you want the enhanced validation back.
window.FIAPP_ENABLE_CUSTOM_VALIDATION = window.FIAPP_ENABLE_CUSTOM_VALIDATION || false;
if (window.FIAPP_ENABLE_CUSTOM_VALIDATION) {
  try {
    document.querySelectorAll('form').forEach(form => {
      form.addEventListener('submit', function(e) {
        try {
          const inputs = this.querySelectorAll('input[required], select[required], textarea[required]');
          let isValid = true;
          let firstEmpty = null;

          inputs.forEach(input => {
            const value = input.value ? input.value.trim() : '';
            if (!value) {
              input.style.borderColor = '#d62828';
              input.style.backgroundColor = '#ffe6e6';
              if (!firstEmpty) firstEmpty = input;
              isValid = false;
            } else {
              input.style.borderColor = '#00b4d8';
              input.style.backgroundColor = '#fff';
            }
          });

          if (!isValid) {
            e.preventDefault();
            showAlert('⚠️ Completa todos los campos', 'error');
            if (firstEmpty) firstEmpty.focus();
            return false;
          }
        } catch (innerErr) {
          console.warn('Error en validación de formulario:', innerErr);
          // No bloquear el envío si la validación falla internamente
        }
      });

      // Limpiar estilo al escribir
      form.querySelectorAll('input, select, textarea').forEach(input => {
        input.addEventListener('input', function() {
          if (this.value.trim()) {
            this.style.borderColor = '#00b4d8';
            this.style.backgroundColor = '#fff';
          }
        });
        input.addEventListener('change', function() {
          if (this.value.trim()) {
            this.style.borderColor = '#00b4d8';
            this.style.backgroundColor = '#fff';
          }
        });
      });
    });
  } catch (err) {
    console.error('Error inicializando validación de formularios:', err);
  }
}

// Show alert function
function showAlert(message, type = 'info') {
  const alert = document.createElement('div');
  alert.className = `alert ${type}`;
  alert.textContent = message;
  alert.style.marginBottom = '1.5rem';
  
  const main = document.querySelector('main');
  if (main) {
    main.insertBefore(alert, main.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      alert.style.opacity = '0';
      alert.style.transition = 'opacity 0.3s ease-out';
      setTimeout(() => alert.remove(), 300);
    }, 5000);
  }
}

// Animate elements on scroll
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll('.card, li, .menu-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(20px)';
  el.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
  observer.observe(el);
});

// Button ripple effect
document.querySelectorAll('button, a.btn').forEach(button => {
  button.addEventListener('click', function(e) {
    const rect = this.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const ripple = document.createElement('span');
    ripple.style.position = 'absolute';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.style.width = '0';
    ripple.style.height = '0';
    ripple.style.borderRadius = '50%';
    ripple.style.background = 'rgba(255, 255, 255, 0.6)';
    ripple.style.pointerEvents = 'none';
    ripple.style.transition = 'width 0.6s, height 0.6s';
    
    this.style.position = 'relative';
    this.style.overflow = 'hidden';
    this.appendChild(ripple);
    
    setTimeout(() => {
      ripple.style.width = '300px';
      ripple.style.height = '300px';
    }, 0);
    
    setTimeout(() => ripple.remove(), 600);
  });
});

// Dark mode toggle (optional)
const darkModeToggle = () => {
  const isDark = localStorage.getItem('darkMode') === 'true';
  if (isDark) {
    document.body.style.filter = 'invert(1) hue-rotate(180deg)';
  }
};

// Initialize tooltips (for future use)
document.querySelectorAll('[title]').forEach(el => {
  el.addEventListener('mouseenter', function() {
    // Could add custom tooltip here
  });
});

// Optional: prevent double submit. Disabled by default to avoid interfering
// with critical flows. Enable by setting `window.FIAPP_PREVENT_DOUBLE_SUBMIT = true`.
window.FIAPP_PREVENT_DOUBLE_SUBMIT = window.FIAPP_PREVENT_DOUBLE_SUBMIT || false;
if (window.FIAPP_PREVENT_DOUBLE_SUBMIT) {
  const submitButtons = document.querySelectorAll('button[type="submit"]');
  submitButtons.forEach(button => {
    button.addEventListener('click', function(e) {
      if (this.dataset.submitted === 'true') {
        e.preventDefault();
        console.log('Prevented double submit on button');
        return;
      }
      this.dataset.submitted = 'true';
      this.disabled = true;
      if (!this.dataset.originalText) this.dataset.originalText = this.textContent;
      this.textContent = 'Enviando...';
      
      setTimeout(() => {
        this.dataset.submitted = 'false';
        this.disabled = false;
        this.textContent = this.dataset.originalText || 'Enviar';
      }, 5000);
    });
  });
}

// Log page load
console.log('%c🎨 FIAPP Web - Modern UI Ready', 'color: #00b4d8; font-size: 14px; font-weight: bold;');

// FIAPP AI chat widget (minimal) — initialize after DOM ready
document.addEventListener('DOMContentLoaded', function() {
  try {
    const role = (document.body && document.body.dataset && document.body.dataset.role) ? document.body.dataset.role : '';
    const chatButton = document.getElementById('fiapp-chat-button');
    const chatModal = document.getElementById('fiapp-chat-modal');
    const chatBackdrop = document.getElementById('fiapp-chat-backdrop');
    const chatClose = document.getElementById('fiapp-chat-close');
    const chatForm = document.getElementById('fiapp-chat-form');
    const chatInput = document.getElementById('fiapp-chat-input');
    const chatMessages = document.getElementById('fiapp-chat-messages');

    console.debug('FIAPP chat init, role=', role, 'chatButtonExists=', !!chatButton, 'chatModalExists=', !!chatModal);

    if (!chatButton || !chatModal) {
      // Elements not present yet or removed — nothing to do
      return;
    }

    // Show the button if the role contains 'tendero' (case-insensitive)
    if (typeof role === 'string' && role.toLowerCase().includes('tendero')) {
      chatButton.classList.remove('hidden');
    }

    function openChat(){
      chatModal.classList.remove('hidden');
      chatModal.setAttribute('aria-hidden','false');
      chatInput && chatInput.focus();
    }

    function closeChat(){
      chatModal.classList.add('hidden');
      chatModal.setAttribute('aria-hidden','true');
    }

    function appendMessage(text, who){
      if (!chatMessages) return;
      const el = document.createElement('div');
      el.className = 'chat-msg ' + (who || 'bot');
      el.textContent = text;
      chatMessages.appendChild(el);
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    async function sendMessageToServer(text){
      appendMessage('⌛ Pensando...', 'system');
      try{
        const r = await fetch('/api/ai_chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text }),
          credentials: 'same-origin'
        });
        const data = await r.json();
        const lastSys = chatMessages.querySelector('.chat-msg.system:last-child');
        if (lastSys) lastSys.remove();
        if (r.ok && data.reply) {
          appendMessage(data.reply, 'bot');
        } else {
          appendMessage(data.error || 'No se recibió respuesta', 'bot');
        }
      }catch(err){
        const lastSys2 = chatMessages.querySelector('.chat-msg.system:last-child');
        if (lastSys2) lastSys2.remove();
        appendMessage('Error de red: ' + (err.message || err), 'bot');
      }
    }

    chatButton.addEventListener('click', openChat);
    chatBackdrop && chatBackdrop.addEventListener('click', closeChat);
    chatClose && chatClose.addEventListener('click', closeChat);

    if (chatForm){
      chatForm.addEventListener('submit', function(e){
        e.preventDefault();
        const text = chatInput.value && chatInput.value.trim();
        if (!text) return;
        appendMessage(text, 'user');
        chatInput.value = '';
        sendMessageToServer(text);
      });
    }
  } catch (err) {
    console.error('Error initializing FIAPP chat widget', err);
  }
});
