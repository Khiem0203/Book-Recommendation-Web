import React, { useEffect, useState } from "react";
import "./Dashboard.css";
import { useNavigate } from "react-router-dom";

function Dashboard() {
    const [overview, setOverview] = useState({ totalUsers: 0, totalBooks: 0 });
    const [query, setQuery] = useState("");
    const [users, setUsers] = useState([]);
    const [books, setBooks] = useState([]);
    const [tokenLogs, setTokenLogs] = useState({ summary: {}, logs: [] });
    const navigate = useNavigate();
    const token = localStorage.getItem("token");

    const fetchOverview = async () => {
        try {
            const [bookRes, userRes] = await Promise.all([
                fetch("http://127.0.0.1:8080/admin/books/count", {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch("http://127.0.0.1:8080/admin/users/search?query=", {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);
            const bookData = await bookRes.json();
            const userData = await userRes.json();
            setOverview({ totalBooks: bookData.total_books, totalUsers: userData.length });
        } catch {
            alert("Không thể lấy dữ liệu hệ thống.");
        }
    };

    const fetchTokenLogs = async () => {
        const res = await fetch("http://127.0.0.1:8080/admin/token-usage", {
            headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setTokenLogs(data);
    };

    const searchUsers = async () => {
        const res = await fetch(`http://127.0.0.1:8080/admin/users/search?query=${query}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setUsers(data);
    };

    const deleteUser = async (id) => {
        await fetch(`http://127.0.0.1:8080/admin/users/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` }
        });
        searchUsers();
    };

    const searchBooks = async () => {
        const res = await fetch(`http://127.0.0.1:8080/admin/books/search?query=${query}`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setBooks(data);
    };

    const deleteBook = async (id) => {
        await fetch(`http://127.0.0.1:8080/admin/books/${id}`, {
            method: "DELETE",
            headers: { Authorization: `Bearer ${token}` }
        });
        searchBooks();
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

    useEffect(() => {
        fetchOverview();
        fetchTokenLogs();
    }, []);

    return (
        <div className="dashboard-container">
            <div className="dashboard-header">
                <h2>Admin Dashboard</h2>
                <button onClick={handleLogout}>Logout</button>
            </div>

            <div className="overview">
                <p><strong>Tổng số user:</strong> {overview.totalUsers}</p>
                <p><strong>Tổng số sách:</strong> {overview.totalBooks}</p>
            </div>

            <div className="search-bar">
                <input
                    type="text"
                    placeholder="Tìm kiếm user hoặc sách"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                />
                <button onClick={searchUsers}>Tìm User</button>
                <button onClick={searchBooks}>Tìm Sách</button>
            </div>

            <div className="section">
                <h3>Danh sách người dùng</h3>
                <ul>
                    {users.map(user => (
                        <li key={user.id}>
                            {user.username} ({user.email})
                            <button onClick={() => deleteUser(user.id)}>Xoá</button>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="section">
                <h3>Danh sách sách (Milvus)</h3>
                <ul>
                    {books.map(book => (
                        <li key={book.id}>
                            {book.title} - {book.author}
                            <button onClick={() => deleteBook(book.id)}>Xoá</button>
                        </li>
                    ))}
                </ul>
            </div>

            <div className="section">
                <h3>Thống kê OpenAI Token</h3>
                <ul>
                    {tokenLogs.summary.by_purpose &&
                        Object.entries(tokenLogs.summary.by_purpose).map(([purpose, usage]) => (
                            <li key={purpose}>
                                <strong>{purpose}</strong>: input = {usage.input}, output = {usage.output}
                            </li>
                        ))}
                </ul>
                <p><strong>Tổng cộng:</strong> {tokenLogs.summary.total_tokens || 0} tokens</p>
            </div>
        </div>
    );
}

export default Dashboard;
