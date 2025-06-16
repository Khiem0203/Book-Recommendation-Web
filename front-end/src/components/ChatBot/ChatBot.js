import React, { useState } from "react";
import "./ChatBot.css";
import SendIcon from "../../assets/Send.svg";

function ChatBot() {
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const sendMessage = async () => {
        if (!input.trim()) return;
        const userMsg = { sender: "user", text: input };
        setMessages((prev) => [...prev, userMsg]);
        setInput("");
        setLoading(true);

        try {
            const res = await fetch("http://127.0.0.1:8080/chatbot-recommend", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: input })
            });
            const data = await res.json();
            const botMsg = { sender: "bot", text: data.reply || "Không trả lời được." };
            setMessages((prev) => [...prev, botMsg]);
        } catch {
            setMessages((prev) => [...prev, { sender: "bot", text: "Lỗi kết nối server." }]);
        }

        setLoading(false);
    };

    return (
        <div className="chatbot-wrapper">
            {isOpen ? (
                <div className="chat-window">
                    <div className="chat-header">
                        <span>Chat với AI</span>
                        <button onClick={() => setIsOpen(false)}>✖</button>
                    </div>
                    <div className="chat-body">
                        {messages.map((msg, i) => (
                            <div key={i} className={`chat-bubble ${msg.sender}`}>
                                {msg.sender === "user" ? `Tôi: ${msg.text}` : `AI: ${msg.text}`}
                            </div>
                        ))}
                        {loading && <div className="chat-bubble bot">Đang trả lời...</div>}
                    </div>
                    <div className="chat-input-area">
                        <input
                            type="text"
                            value={input}
                            placeholder="Nhập..."
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
                        />
                        <button onClick={sendMessage}>
                            <img src={SendIcon} alt="Gửi" width={20} />
                        </button>
                    </div>
                </div>
            ) : (
                <button className="open-chat-btn" onClick={() => setIsOpen(true)}>Chat với AI</button>
            )}
        </div>
    );
}

export default ChatBot;
