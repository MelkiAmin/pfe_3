<script setup lang="ts">
import { useAuthStore } from '@/stores/auth'
import type { EventListItem } from '@/services/api'

interface ChatMessage {
  id: number
  role: 'user' | 'bot'
  content: string
  events?: EventListItem[]
  timestamp: Date
}

interface ChatbotResponse {
  reply?: string
  response?: string
  events?: EventListItem[]
  detected_category?: string | null
}

const authStore = useAuthStore()
const isOpen = ref(false)
const messages = ref<ChatMessage[]>([
  {
    id: 1,
    role: 'bot',
    content: 'Bonjour ! Je suis votre assistant événementiel. Dites-moi quel type d\'événement vous intéresse (concert, sport, business, culture...) et je vous recommande les meilleurs événements !',
    timestamp: new Date(),
  },
])
const userMessage = ref('')
const isLoading = ref(false)
const messagesContainer = ref<HTMLElement | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

const canShowChatbot = computed(() => {
  const role = authStore.role
  const isAttendee = role === 'attendee' || role === 'utilisateur' || !role
  return isAttendee
})

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = async () => {
  if (!userMessage.value.trim() || isLoading.value) return

  const msg = userMessage.value.trim()
  userMessage.value = ''
  isLoading.value = true

  const userMsg: ChatMessage = {
    id: Date.now(),
    role: 'user',
    content: msg,
    timestamp: new Date(),
  }
  messages.value.push(userMsg)
  scrollToBottom()

  try {
    console.log('[Chatbot] Sending message:', msg)
    const response = await fetch('/api/events/chatbot/chat/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg }),
    })

    console.log('[Chatbot] Response status:', response.status)

    if (!response.ok) {
      const errorText = await response.text()
      console.error('[Chatbot] HTTP Error:', response.status, errorText)
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const data: ChatbotResponse = await response.json()
    console.log('[Chatbot] Response data:', data)

    const replyContent = data.reply || data.response
    if (!replyContent) {
      console.error('[Chatbot] Invalid response: missing reply/response field')
      throw new Error('Réponse invalide du serveur')
    }

    const botMsg: ChatMessage = {
      id: Date.now() + 1,
      role: 'bot',
      content: replyContent,
      events: data.events,
      timestamp: new Date(),
    }
    messages.value.push(botMsg)
  }
  catch (error: any) {
    console.error('[Chatbot] Error:', error.message || error)

    const errorMessage = error?.response?.data?.detail
      || error?.message
      || 'Désolé, je rencontre des difficultés techniques. Veuillez réessayer.'

    const errorMsg: ChatMessage = {
      id: Date.now() + 1,
      role: 'bot',
      content: errorMessage,
      timestamp: new Date(),
    }
    messages.value.push(errorMsg)
  }
  finally {
    isLoading.value = false
    scrollToBottom()
    inputRef.value?.focus()
  }
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })
}
</script>

<template>
  <Teleport to="body">
    <div v-if="canShowChatbot" class="chatbot-wrapper">
      <Transition name="fade-scale">
        <button
          v-if="!isOpen"
          class="chatbot-fab"
          aria-label="Ouvrir le chat"
          @click="isOpen = true"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="28"
            height="28"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          >
            <path d="M12 2A2 2 0 0 1 14 4V8.5L17.5 12L14 15.5V20A2 2 0 0 1 10 22H2A2 2 0 0 1 0 20V4A2 2 0 0 1 2 2Z" />
            <path d="M12 8.5L8 12L12 15.5" />
            <path d="M16 12L12 8.5" />
          </svg>
        </button>
      </Transition>

      <Transition name="chat-slide">
        <div v-if="isOpen" class="chatbot-window">
          <header class="chatbot-header">
            <div class="chatbot-header-left">
              <div class="chatbot-avatar">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="24"
                  height="24"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M12 2A2 2 0 0 1 14 4V8.5L17.5 12L14 15.5V20A2 2 0 0 1 10 22H2A2 2 0 0 1 0 20V4A2 2 0 0 1 2 2Z" />
                  <path d="M12 8.5L8 12L12 15.5" />
                  <path d="M16 12L12 8.5" />
                </svg>
              </div>
              <div class="chatbot-header-info">
                <span class="chatbot-title">Assistant IA</span>
                <span class="chatbot-status">
                  <span class="status-dot"></span>
                  En ligne
                </span>
              </div>
            </div>
            <button
              class="chatbot-close"
              aria-label="Fermer le chat"
              @click="isOpen = false"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </header>

          <div ref="messagesContainer" class="chatbot-messages">
            <div
              v-for="msg in messages"
              :key="msg.id"
              :class="['message', `message--${msg.role}`]"
            >
              <div
                v-if="msg.role === 'bot'"
                class="message-avatar"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M12 2A2 2 0 0 1 14 4V8.5L17.5 12L14 15.5V20A2 2 0 0 1 10 22H2A2 2 0 0 1 0 20V4A2 2 0 0 1 2 2Z" />
                </svg>
              </div>

              <div class="message-bubble">
                <p class="message-text">{{ msg.content }}</p>

                <div
                  v-if="msg.events && msg.events.length > 0"
                  class="message-events"
                >
                  <div
                    v-for="event in msg.events"
                    :key="event.id"
                    class="event-card"
                  >
                    <span class="event-title">{{ event.title }}</span>
                    <span class="event-info">
                      {{ new Date(event.start_date).toLocaleDateString('fr-FR') }}
                      · {{ event.city || 'En ligne' }}
                    </span>
                    <a
                      :href="`/events/${event.slug}`"
                      class="event-link"
                    >
                      Voir l'événement
                    </a>
                  </div>
                </div>

                <span class="message-time">{{ formatTime(msg.timestamp) }}</span>
              </div>
            </div>

            <div
              v-if="isLoading"
              class="message message--bot"
            >
              <div class="message-avatar">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                >
                  <path d="M12 2A2 2 0 0 1 14 4V8.5L17.5 12L14 15.5V20A2 2 0 0 1 10 22H2A2 2 0 0 1 0 20V4A2 2 0 0 1 2 2Z" />
                </svg>
              </div>
              <div class="message-bubble">
                <div class="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>

          <footer class="chatbot-footer">
            <input
              ref="inputRef"
              v-model="userMessage"
              type="text"
              class="chatbot-input"
              placeholder="Tapez votre message..."
              :disabled="isLoading"
              @keyup.enter="sendMessage"
            />
            <button
              class="chatbot-send"
              :disabled="!userMessage.trim() || isLoading"
              aria-label="Envoyer"
              @click="sendMessage"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="20"
                height="20"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <line x1="22" y1="2" x2="11" y2="13" />
                <polygon points="22 2 15 22 11 13 2 9 22 2" />
              </svg>
            </button>
          </footer>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<style scoped>
.chatbot-wrapper {
  position: fixed;
  right: 24px;
  bottom: 90px;
  z-index: 9999;
  display: flex;
  flex-direction: column-reverse;
  align-items: flex-end;
  gap: 16px;
}

.chatbot-fab {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #7367f0 0%, #9b95f5 100%);
  color: white;
  cursor: pointer;
  box-shadow: 0 8px 24px rgba(115, 103, 240, 0.4);
  transition: transform 0.25s cubic-bezier(0.34, 1.56, 0.64, 1),
              box-shadow 0.25s ease, background 0.25s ease;
  animation: fab-appear 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes fab-appear {
  0% {
    opacity: 0;
    transform: scale(0.5) translateY(20px);
  }
  100% {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.chatbot-fab:hover {
  transform: scale(1.12);
  box-shadow: 0 12px 36px rgba(115, 103, 240, 0.5);
}

.chatbot-fab:active {
  transform: scale(0.95);
}

.chatbot-fab svg {
  animation: icon-pulse 2s ease-in-out infinite;
}

@keyframes icon-pulse {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
}

.chatbot-window {
  width: 380px;
  max-height: 580px;
  border-radius: 20px;
  background: #fff;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.15),
              0 0 0 1px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chatbot-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: linear-gradient(135deg, #7367f0 0%, #9b95f5 100%);
  color: white;
}

.chatbot-header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.chatbot-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.chatbot-header-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.chatbot-title {
  font-size: 16px;
  font-weight: 600;
}

.chatbot-status {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  opacity: 0.9;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #10b981;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.7; transform: scale(0.9); }
}

.chatbot-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  cursor: pointer;
  transition: background 0.2s ease;
}

.chatbot-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.chatbot-messages {
  flex: 1;
  min-height: 280px;
  max-height: 380px;
  overflow-y: auto;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  background: #f8f9fa;
}

.chatbot-messages::-webkit-scrollbar {
  width: 6px;
}

.chatbot-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chatbot-messages::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.15);
  border-radius: 3px;
}

.message {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  animation: message-appear 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

@keyframes message-appear {
  0% {
    opacity: 0;
    transform: translateY(10px) scale(0.95);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.message--user {
  flex-direction: row-reverse;
}

.message-avatar {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7367f0 0%, #9b95f5 100%);
  color: white;
}

.message-bubble {
  display: flex;
  flex-direction: column;
  gap: 4px;
  max-width: 75%;
}

.message-text {
  padding: 12px 16px;
  border-radius: 18px;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
  word-wrap: break-word;
}

.message--user .message-text {
  background: linear-gradient(135deg, #7367f0 0%, #9b95f5 100%);
  color: white;
  border-bottom-right-radius: 6px;
}

.message--bot .message-text {
  background: white;
  color: #2d3748;
  border-bottom-left-radius: 6px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.message-events {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.event-card {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
}

.event-title {
  font-size: 14px;
  font-weight: 600;
  color: #2d3748;
}

.event-info {
  font-size: 12px;
  color: #718096;
}

.event-link {
  display: inline-block;
  margin-top: 6px;
  padding: 6px 12px;
  background: rgba(115, 103, 240, 0.1);
  color: #7367f0;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: background 0.2s ease;
}

.event-link:hover {
  background: rgba(115, 103, 240, 0.2);
}

.message-time {
  font-size: 11px;
  color: #a0aec0;
  margin-top: 2px;
}

.message--user .message-time {
  text-align: right;
}

.typing-indicator {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 14px 18px;
  background: white;
  border-radius: 18px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.typing-indicator span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #7367f0 0%, #9b95f5 100%);
  animation: typing 1.4s ease-in-out infinite;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes typing {
  0%, 100% {
    transform: translateY(0) scale(0.8);
    opacity: 0.5;
  }
  50% {
    transform: translateY(-8px) scale(1);
    opacity: 1;
  }
}

.chatbot-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.chatbot-input {
  flex: 1;
  padding: 12px 18px;
  border: 2px solid #e2e8f0;
  border-radius: 24px;
  font-size: 14px;
  color: #1a202c;
  background: #ffffff;
  outline: none;
  transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.2s ease;
}

.chatbot-input:focus {
  border-color: #7367f0;
  background: #ffffff;
  box-shadow: 0 0 0 4px rgba(115, 103, 240, 0.1);
}

.chatbot-input::placeholder {
  color: #a0aec0;
  opacity: 1;
}

.chatbot-input:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.chatbot-input:-webkit-autofill,
.chatbot-input:-webkit-autofill:hover,
.chatbot-input:-webkit-autofill:focus {
  -webkit-text-fill-color: #1a202c;
  -webkit-box-shadow: 0 0 0px 1000px #ffffff inset;
  transition: background-color 5000s ease-in-out 0s;
}

.chatbot-send {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  min-width: 48px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #7367f0 0%, #9b95f5 100%);
  color: white;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease, opacity 0.2s ease;
}

.chatbot-send:hover:not(:disabled) {
  transform: scale(1.08);
  box-shadow: 0 4px 16px rgba(115, 103, 240, 0.5);
}

.chatbot-send:active:not(:disabled) {
  transform: scale(0.95);
}

.chatbot-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.fade-scale-enter-active,
.fade-scale-leave-active {
  transition: all 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.fade-scale-enter-from {
  opacity: 0;
  transform: scale(0.5) translateY(15px);
}

.fade-scale-leave-to {
  opacity: 0;
  transform: scale(0.8);
}

.chat-slide-enter-active {
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.chat-slide-leave-active {
  transition: all 0.2s ease-in;
}

.chat-slide-enter-from {
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}

.chat-slide-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.95);
}

@media (max-width: 480px) {
  .chatbot-wrapper {
    right: 12px;
    left: 12px;
    bottom: 70px;
    align-items: stretch;
  }

  .chatbot-window {
    width: 100%;
    max-height: 75vh;
  }

  .chatbot-fab {
    width: 52px;
    height: 52px;
    align-self: flex-end;
  }

  .chatbot-messages {
    min-height: 200px;
    max-height: 50vh;
  }
}
</style>