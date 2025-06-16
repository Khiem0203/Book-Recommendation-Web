import React, { useState } from "react";
import "./Login.css";
import { useNavigate } from "react-router-dom";

function AdminLogin() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const response = await fetch("http://127.0.0.1:8080/admin/login/", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ identifier: username, password })
            });
            const data = await response.json();
            if (response.ok && data.access_token) {
                localStorage.setItem("token", data.access_token);
                setErrorMessage("");
                navigate("/dashboard");
            } else {
                setErrorMessage(data.detail || "Đăng nhập thất bại");
            }
        } catch {
            setErrorMessage("Lỗi kết nối máy chủ");
        }
    };

    return (
        <div className="admin-login-container">
            <div className="admin-login-card">
                <h2>Admin Login</h2>
                <input
                    type="text"
                    placeholder="Username hoặc Email"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                />
                <input
                    type="password"
                    placeholder="Mật khẩu"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                />
                {errorMessage && <p className="error">{errorMessage}</p>}
                <button onClick={handleLogin}>Đăng Nhập</button>
            </div>
        </div>
    );
}

export default AdminLogin;
