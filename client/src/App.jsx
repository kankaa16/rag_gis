import { useState, useEffect } from "react"
import ChatContainer from "./components/ChatContainer"
import ChatInput from "./components/ChatInput"
import Header from "./components/Header"
import "./App.css"

function App() {

  const [messages, setMessages] = useState(() => {
    const saved = localStorage.getItem("chat_messages")
    return saved ? JSON.parse(saved) : []
  })

  const [isMuted, setIsMuted] = useState(false)

  useEffect(() => {
    localStorage.setItem("chat_messages", JSON.stringify(messages))
  }, [messages])

  const clearChat = () => {
    setMessages([])
    localStorage.removeItem("chat_messages")
  }

  const toggleMute = () => {
    setIsMuted(!isMuted)

    if (!isMuted) {
      window.speechSynthesis.cancel()
    }
  }

  const sendMessage = async (text) => {

    const userMsg = { role: "user", content: text }

    setMessages(prev => [...prev, userMsg])

    try {

      const res = await fetch("http://localhost:8000/ask", {
        method:"POST",
        headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ question:text })
      })

      const data = await res.json()

      const botMsg = { role:"assistant", content:data.answer }

      setMessages(prev => [...prev, botMsg])

      if(!isMuted){

        const cleanText = data.answer.replace(/[*#_]/g,"")

        const utterance = new SpeechSynthesisUtterance(cleanText)

        utterance.rate = 0.9
        utterance.pitch = 0.9

        window.speechSynthesis.speak(utterance)
      }

    } catch(error){
      console.error("Backend error:", error)
    }
  }

  return(
    <div className="app">

      <Header
        clearChat={clearChat}
        isMuted={isMuted}
        toggleMute={toggleMute}
      />

      <ChatContainer messages={messages}/>

      <ChatInput sendMessage={sendMessage}/>

    </div>
  )
}

export default App