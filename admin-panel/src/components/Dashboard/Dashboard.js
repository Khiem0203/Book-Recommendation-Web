import React, { useEffect, useState, useCallback } from "react";
import "./Dashboard.css";
import { useNavigate } from "react-router-dom";

function Dashboard() {
    const [overview, setOverview] = useState({ totalUsers: 0, totalBooks: 0 });
    const [userQuery, setUserQuery] = useState("");
    const [bookQuery, setBookQuery] = useState("");
    const [users, setUsers] = useState([]);
    const [books, setBooks] = useState([]);
    const [tokenLogs, setTokenLogs] = useState({});
    const [uploading, setUploading] = useState(false);
    const [progress, setProgress] = useState(0);
    const [collections, setCollections] = useState([]);
    const [selectedCollection, setSelectedCollection] = useState("");
    const [customCollection, setCustomCollection] = useState("");
    const navigate = useNavigate();
    const token = localStorage.getItem("token");

    const fetchOverview = useCallback(async () => {
        const [bookRes, userRes] = await Promise.all([
            fetch("http://127.0.0.1:8080/admin/books/count", {
                headers: { Authorization: `Bearer ${token}` }
            }),
            fetch("http://127.0.0.1:8080/admin/users", {
                headers: { Authorization: `Bearer ${token}` }
            })
        ]);
        const bookData = await bookRes.json();
        const userData = await userRes.json();
        setOverview({ totalBooks: bookData.total_books, totalUsers: userData.length });
    }, [token]);

    const fetchTokenLogs = useCallback(async () => {
        const res = await fetch("http://127.0.0.1:8080/admin/token-usage", {
            headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setTokenLogs(data.summary.by_purpose || {});
    }, [token]);

    const fetchCollections = useCallback(async () => {
        const res = await fetch("http://127.0.0.1:8080/admin/collections", {
            headers: { Authorization: `Bearer ${token}` }
        });
        const data = await res.json();
        setCollections(data.collections || []);
    }, [token]);

    const searchUsers = async () => {
        const res = await fetch(`http://127.0.0.1:8080/admin/users/search?query=${userQuery}`, {
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
        const res = await fetch(`http://127.0.0.1:8080/admin/books/search?query=${bookQuery}`, {
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

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        const formData = new FormData();
        const collectionName = customCollection || selectedCollection;
        if (!collectionName) return alert("Vui lòng chọn hoặc nhập tên collection");
        formData.append("file", file);
        formData.append("collection_name", collectionName);
        setUploading(true);
        setProgress(0);
        const interval = setInterval(() => {
            setProgress((prev) => (prev < 90 ? prev + 10 : prev));
        }, 300);
        try {
            const res = await fetch("http://127.0.0.1:8080/admin/upload-books", {
                method: "POST",
                headers: { Authorization: `Bearer ${token}` },
                body: formData
            });
            const data = await res.json();
            clearInterval(interval);
            setProgress(100);
            setTimeout(() => setUploading(false), 1000);
            alert(data.message || "Upload xong");
        } catch {
            clearInterval(interval);
            setUploading(false);
            alert("Lỗi khi upload file.");
        }
    };

    const handleLogout = () => {
        localStorage.removeItem("token");
        navigate("/");
    };

    useEffect(() => {
        fetchOverview();
        fetchTokenLogs();
        fetchCollections();
    }, [fetchOverview, fetchTokenLogs, fetchCollections]);

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
            <div className="section">
                <h3>Tìm kiếm người dùng</h3>
                <input
                    type="text"
                    placeholder="Tìm kiếm user"
                    value={userQuery}
                    onChange={(e) => setUserQuery(e.target.value)}
                />
                <button onClick={searchUsers}>Tìm User</button>
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
                <h3>Tìm kiếm sách</h3>
                <input
                    type="text"
                    placeholder="Tìm kiếm sách"
                    value={bookQuery}
                    onChange={(e) => setBookQuery(e.target.value)}
                />
                <button onClick={searchBooks}>Tìm Sách</button>
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
                <h3>Upload Database (CSV)</h3>
                <label>Chọn collection có sẵn:</label>
                <select value={selectedCollection} onChange={(e) => setSelectedCollection(e.target.value)}>
                    <option value="">-- Chọn --</option>
                    {collections.map((c, i) => (
                        <option key={i} value={c}>{c}</option>
                    ))}
                </select>
                <label>Hoặc nhập tên collection mới:</label>
                <input
                    type="text"
                    placeholder="Tên collection mới"
                    value={customCollection}
                    onChange={(e) => setCustomCollection(e.target.value)}
                />
                <input type="file" accept=".csv" onChange={handleFileUpload} />
                {uploading && (
                    <div className="progress-container">
                        <div className="progress-bar" style={{ width: `${progress}%` }} />
                        <p>Đang upload và xử lý... {progress}%</p>
                    </div>
                )}
            </div>
            <div className="section token-stats">
                <h3>Thống kê OpenAI Token</h3>
                <ul>
                    <li><strong>Embedding</strong>: input = {tokenLogs.embedding?.input || 0}, output = {tokenLogs.embedding?.output || 0}</li>
                    <li><strong>Query</strong>: input = {tokenLogs.bookrcm?.input || 0}, output = {tokenLogs.bookrcm?.output || 0}</li>
                    <li><strong>Explanation</strong>: input = {tokenLogs.explanation?.input || 0}, output = {tokenLogs.explanation?.output || 0}</li>
                    <li><strong>Chatbot</strong>: input = {tokenLogs.chatbot?.input || 0}, output = {tokenLogs.chatbot?.output || 0}</li>
                </ul>
                <p><strong>Tổng cộng:</strong> {
                    Object.values(tokenLogs).reduce((sum, p) =>
                        sum + (p.input || 0) + (p.output || 0), 0)
                } tokens</p>
            </div>
        </div>
    );
}

export default Dashboard;
