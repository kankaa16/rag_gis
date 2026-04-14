import { useEffect, useRef } from "react"

function ChatContainer({messages}){

const bottomRef = useRef(null)

useEffect(()=>{
  bottomRef.current?.scrollIntoView({behavior:"smooth"})
},[messages])

return(
  <div className="chat-container">

    {messages.map((msg,i)=>(
      <div key={i} className={`message-row ${msg.role==="user"?"user":"bot"}`}>

        {msg.role==="assistant" && (
          <div className="avatar">AI</div>
        )}

        <div className="message-bubble">
          {msg.content}
        </div>

        {msg.role==="user" && (
          <div className="avatar">U</div>
        )}

      </div>
    ))}

    <div ref={bottomRef}></div>

  </div>
)
}

export default ChatContainer