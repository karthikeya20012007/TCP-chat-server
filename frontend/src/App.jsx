import { useEffect, useState } from "react";

function App() {
  const [username, setUsername] = useState("");

  const [tempUsername, setTempUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [isLoggedIn, setIsLoggedIn] =
    useState(false);

  const [socket, setSocket] = useState(null);

  const [message, setMessage] = useState("");

  const [messages, setMessages] = useState([]);

  const [onlineUsers, setOnlineUsers] = useState([]);

  const [authMessage, setAuthMessage] = useState("");

  const connectWebSocket = () => {
    const ws = new WebSocket(
      "ws://localhost:8000/ws"
    );

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          type: "join",
          username: tempUsername
        })
      );
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(
        event.data
      );

      if (data.type === "chat") {
        setMessages((prev) => [
          ...prev,
          data.message
        ]);
      }

      if (data.type === "history") {
        setMessages((prev) => [
          ...prev,
          data.message
        ]);
      }

      if (data.type === "users") {
        setOnlineUsers(data.users);
      }
    };

    setSocket(ws);

    setUsername(tempUsername);

    setIsLoggedIn(true);
  };

  const handleLogin = async () => {
    if (
      !tempUsername.trim() ||
      !password.trim()
    ) {
      setAuthMessage(
        "Enter username and password"
      );

      return;
    }

    try {
      const response = await fetch(
        "http://localhost:8000/login",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            username: tempUsername,
            password
          })
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        setAuthMessage(data.detail);

        return;
      }

      setAuthMessage("");

      connectWebSocket();

    } catch (error) {
      setAuthMessage(
        "Login failed"
      );
    }
  };

  const handleRegister = async () => {
    if (
      !tempUsername.trim() ||
      !password.trim()
    ) {
      setAuthMessage(
        "Enter username and password"
      );

      return;
    }

    try {
      const response = await fetch(
        "http://localhost:8000/register",
        {
          method: "POST",

          headers: {
            "Content-Type":
              "application/json"
          },

          body: JSON.stringify({
            username: tempUsername,
            password
          })
        }
      );

      const data =
        await response.json();

      if (!response.ok) {
        setAuthMessage(data.detail);

        return;
      }

      setAuthMessage(data.message);

      connectWebSocket();

    } catch (error) {
      setAuthMessage("Registration failed");
    }
  };

  const sendMessage = () => {
    if (!message.trim()) {
      return;
    }

    socket.send(
      JSON.stringify({
        type: "chat",
        username,
        content: message
      })
    );

    setMessage("");
  };

  if (!isLoggedIn) {
    return (
      <div style={styles.loginContainer}>
        <div style={styles.loginBox}>
          <h1 style={styles.chatHeader}>
            Realtime Chat
          </h1>

          <input
            type="text"
            placeholder="Username"
            value={tempUsername}
            onChange={(e) =>
              setTempUsername(
                e.target.value
              )
            }
            style={styles.input}
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            style={styles.input}
          />

          {
            authMessage && (
              <div
                style={{
                  color: "#38bdf8",
                  textAlign: "center",
                  fontSize: "14px"
                }}
              >
                {authMessage}
              </div>
            )
          }

          <div
            style={{
              display: "flex",
              gap: "10px"
            }}
          >
            <button
              onClick={handleLogin}
              style={{
                ...styles.button,
                flex: 1
              }}
            >
              Login
            </button>

            <button
              onClick={handleRegister}
              style={{
                ...styles.button,
                flex: 1,
                background: "#16a34a"
              }}
            >
              Register
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.app}>
      <div style={styles.chatContainer}>
        <div style={styles.chatHeader}>
          Realtime Chat
        </div>

        <div style={styles.messages}>
          {messages.map((msg, index) => (
            <div
              key={index}
              style={styles.message}
            >
              {msg}
            </div>
          ))}
        </div>

        <div style={styles.inputArea}>
          <input
            type="text"
            value={message}
            onChange={(e) =>
              setMessage(e.target.value)
            }
            style={styles.chatInput}
          />

          <button
            onClick={sendMessage}
            style={styles.button}
          >
            Send
          </button>
        </div>
      </div>

      <div style={styles.sidebar}>
        <h2>Online Users</h2>

        {onlineUsers.map((user, index) => (
          <div
            key={index}
            style={styles.user}
          >
            {user}
          </div>
        ))}
      </div>
    </div>
  );
}

const styles = {
  loginContainer: {
    height: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    background: "#0f172a",
    color: "white"
  },

  loginBox: {
    display: "flex",
    flexDirection: "column",
    gap: "20px",
    width: "320px",
    padding: "30px",
    background: "#111827",
    borderRadius: "12px"
  },

  app: {
    display: "flex",
    height: "100vh",
    background: "#0f172a",
    color: "white"
  },

  chatContainer: {
    flex: 1,
    display: "flex",
    flexDirection: "column",
    padding: "20px"
  },

  chatHeader: {
    fontSize: "48px",
    fontWeight: "bold",
    marginBottom: "20px",
    textAlign: "center",
    lineHeight: "1.1",
    whiteSpace: "nowrap"
  },

  messages: {
    flex: 1,
    border: "1px solid #334155",
    padding: "15px",
    overflowY: "scroll",
    borderRadius: "10px",
    background: "#111827"
  },

  message: {
    padding: "10px",
    marginBottom: "10px",
    background: "#1e293b",
    borderRadius: "8px"
  },

  inputArea: {
    display: "flex",
    gap: "10px",
    marginTop: "15px"
  },

  input: {
    padding: "14px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "none",
    outline: "none"
  },

  chatInput: {
    flex: 1,
    padding: "12px",
    fontSize: "16px",
    borderRadius: "8px",
    border: "none"
  },

  button: {
    padding: "12px 20px",
    fontSize: "16px",
    border: "none",
    borderRadius: "8px",
    background: "#2563eb",
    color: "white",
    cursor: "pointer"
  },

  sidebar: {
    width: "250px",
    background: "#111827",
    padding: "20px",
    borderLeft: "1px solid #334155"
  },

  user: {
    padding: "10px",
    marginTop: "10px",
    background: "#1e293b",
    borderRadius: "8px"
  }
};

export default App;