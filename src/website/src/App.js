import React, { useState, useEffect, useRef } from "react";

// --- LOGIN FORM COMPONENT ---
function LoginForm({ onLoginSuccess }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();

    // Simple validation
    if (!email || !password) {
      setError("Both fields are required");
      return;
    }

    // Dummy authentication logic
    if (email === "test@example.com" && password === "password") {
      onLoginSuccess();
    } else {
      setError("Invalid email or password");
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#121212", // Dark background
        color: "#ffffff", // White text
        fontFamily: "'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif",
      }}
    >
      <div
        style={{
          backgroundColor: "#1e1e1e", // Dark gray card
          padding: "30px",
          borderRadius: "12px",
          boxShadow: "0px 6px 16px rgba(0,0,0,0.3)",
          width: "320px",
          textAlign: "center",
          border: "1px solid #333333",
        }}
      >
        <h2 style={{ marginBottom: "20px", color: "#f0f0f0" }}>Login</h2>
        {error && <p style={{ color: "#ff5555", margin: "10px 0" }}>{error}</p>}
        <form onSubmit={handleSubmit}>
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            style={{
              width: "100%",
              padding: "12px",
              margin: "8px 0",
              borderRadius: "6px",
              border: "1px solid #444",
              backgroundColor: "#252525",
              color: "#ffffff",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={{
              width: "100%",
              padding: "12px",
              margin: "8px 0",
              borderRadius: "6px",
              border: "1px solid #444",
              backgroundColor: "#252525",
              color: "#ffffff",
              fontSize: "14px",
              boxSizing: "border-box",
            }}
          />
          <button
            type="submit"
            style={{
              width: "100%",
              padding: "12px",
              margin: "16px 0 8px",
              borderRadius: "6px",
              border: "none",
              backgroundColor: "#3a6ea5", // Darker blue
              color: "white",
              cursor: "pointer",
              fontSize: "14px",
              fontWeight: "bold",
              transition: "background-color 0.2s",
            }}
            onMouseOver={(e) => (e.target.style.backgroundColor = "#457ab8")}
            onMouseOut={(e) => (e.target.style.backgroundColor = "#3a6ea5")}
          >
            Continue
          </button>
        </form>
      </div>
    </div>
  );
}

// --- PATTERN LOCK COMPONENT ---
function PatternLockScreen({ onSuccess }) {
  // Example correct pattern (indices of circles): top-left→top-middle→top-right→middle-right→bottom-right
  const CORRECT_PATTERN = [0, 1, 2, 5, 8];

  const [pattern, setPattern] = useState([]);
  const [isMouseDown, setIsMouseDown] = useState(false);
  const [error, setError] = useState("");
  const [circlePositions, setCirclePositions] = useState([]);
  const [currentPos, setCurrentPos] = useState({ x: 0, y: 0 });
  
  const gridRef = useRef(null);
  const circleRefs = useRef([]);

  // Initialize circle refs
  useEffect(() => {
    circleRefs.current = circleRefs.current.slice(0, 9);
  }, []);

  // Update circle positions when they're available
  useEffect(() => {
    if (circleRefs.current.length === 9 && circleRefs.current.every(ref => ref)) {
      const positions = circleRefs.current.map(ref => {
        const rect = ref.getBoundingClientRect();
        return {
          x: rect.left + rect.width / 2,
          y: rect.top + rect.height / 2
        };
      });
      setCirclePositions(positions);
    }
  }, [gridRef.current]);

  // Track mouse/touch position
  const handleMouseMove = (e) => {
    if (isMouseDown) {
      setCurrentPos({ x: e.clientX, y: e.clientY });
    }
  };

  const handleTouchMove = (e) => {
    if (isMouseDown && e.touches && e.touches[0]) {
      setCurrentPos({ 
        x: e.touches[0].clientX, 
        y: e.touches[0].clientY 
      });
    }
  };

  // Check the pattern when the user releases the mouse and has drawn something
  useEffect(() => {
    if (!isMouseDown && pattern.length > 0) {
      // Compare array contents
      if (JSON.stringify(pattern) === JSON.stringify(CORRECT_PATTERN)) {
        onSuccess();
      } else {
        setError("Incorrect pattern. Try again!");
        // Reset the pattern after a short delay
        setTimeout(() => {
          setPattern([]);
          setError("");
        }, 1000);
      }
    }
  }, [isMouseDown, pattern, onSuccess]);

  const handleCircleEnter = (index) => {
    if (isMouseDown) {
      // Add the index only if not already in the pattern
      if (!pattern.includes(index)) {
        setPattern((prev) => [...prev, index]);
      }
    }
  };

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        height: "100vh",
        backgroundColor: "#121212",
        color: "#ffffff",
        fontFamily: "'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif",
      }}
      onMouseMove={handleMouseMove}
      onTouchMove={handleTouchMove}
    >
      <div
        style={{
          backgroundColor: "#1e1e1e",
          padding: "30px",
          borderRadius: "12px",
          boxShadow: "0px 6px 16px rgba(0,0,0,0.3)",
          maxWidth: "350px",
          width: "100%",
          textAlign: "center",
          border: "1px solid #333333",
        }}
      >
        <h2 style={{ marginBottom: "20px", color: "#f0f0f0" }}>
          Enter Pattern
        </h2>
        <p style={{ marginBottom: "20px", color: "#aaaaaa", fontSize: "14px" }}>
          Draw your security pattern to continue
        </p>

        <div
          ref={gridRef}
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "20px",
            width: "240px",
            margin: "0 auto",
            padding: "20px 0",
            position: "relative",
          }}
        >
          {/* SVG for drawing lines between dots */}
          <svg
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: "100%",
              pointerEvents: "none",
              zIndex: 5,
            }}
          >
            {/* Lines connecting selected circles */}
            {pattern.length > 1 &&
              pattern.slice(0, -1).map((fromIndex, i) => {
                const toIndex = pattern[i + 1];
                if (
                  circlePositions[fromIndex] &&
                  circlePositions[toIndex]
                ) {
                  const from = circlePositions[fromIndex];
                  const to = circlePositions[toIndex];
                  return (
                    <line
                      key={`line-${i}`}
                      x1={from.x - gridRef.current.getBoundingClientRect().left}
                      y1={from.y - gridRef.current.getBoundingClientRect().top}
                      x2={to.x - gridRef.current.getBoundingClientRect().left}
                      y2={to.y - gridRef.current.getBoundingClientRect().top}
                      stroke="#3a6ea5"
                      strokeWidth="3"
                      strokeLinecap="round"
                    />
                  );
                }
                return null;
              })}

            {/* Line from last selected circle to current mouse position */}
            {isMouseDown && pattern.length > 0 && circlePositions[pattern[pattern.length - 1]] && (
              <line
                x1={circlePositions[pattern[pattern.length - 1]].x - gridRef.current.getBoundingClientRect().left}
                y1={circlePositions[pattern[pattern.length - 1]].y - gridRef.current.getBoundingClientRect().top}
                x2={currentPos.x - gridRef.current.getBoundingClientRect().left}
                y2={currentPos.y - gridRef.current.getBoundingClientRect().top}
                stroke="#3a6ea5"
                strokeWidth="3"
                strokeLinecap="round"
                strokeOpacity="0.6"
              />
            )}
          </svg>

          {Array.from({ length: 9 }, (_, index) => (
            <div
              key={index}
              ref={(el) => (circleRefs.current[index] = el)}
              onMouseDown={(e) => {
                setIsMouseDown(true);
                setPattern([index]);
                setCurrentPos({ x: e.clientX, y: e.clientY });
              }}
              onMouseEnter={() => handleCircleEnter(index)}
              onMouseUp={() => setIsMouseDown(false)}
              // Touch events for mobile
              onTouchStart={(e) => {
                setIsMouseDown(true);
                setPattern([index]);
                if (e.touches && e.touches[0]) {
                  setCurrentPos({ 
                    x: e.touches[0].clientX, 
                    y: e.touches[0].clientY 
                  });
                }
              }}
              onTouchEnd={() => setIsMouseDown(false)}
              style={{
                width: "60px",
                height: "60px",
                borderRadius: "50%",
                border: "2px solid #444",
                backgroundColor: pattern.includes(index) 
                  ? "#3a6ea5" 
                  : "#252525",
                cursor: "pointer",
                display: "flex",
                justifyContent: "center",
                alignItems: "center",
                transition: "background-color 0.2s, transform 0.1s",
                transform: pattern.includes(index) ? "scale(1.05)" : "scale(1)",
                zIndex: 10,
                position: "relative",
              }}
            >
              {pattern.includes(index) && (
                <div
                  style={{
                    width: "20px",
                    height: "20px",
                    borderRadius: "50%",
                    backgroundColor: "#ffffff",
                  }}
                />
              )}
            </div>
          ))}
        </div>
        
        {error && (
          <div style={{ color: "#ff5555", marginTop: "20px", fontSize: "14px" }}>
            {error}
          </div>
        )}
        
        <button
          onClick={() => {
            setPattern([]);
            setError("");
          }}
          style={{
            padding: "10px 20px",
            margin: "20px 0 0",
            borderRadius: "6px",
            border: "1px solid #444",
            backgroundColor: "transparent",
            color: "#aaaaaa",
            cursor: "pointer",
            fontSize: "14px",
            transition: "background-color 0.2s",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#252525")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "transparent")}
        >
          Reset
        </button>
      </div>
    </div>
  );
}

// --- MAIN APP COMPONENT ---
function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showPatternLock, setShowPatternLock] = useState(false);

  // Called by the Login form when username/password check is successful
  const handleLoginSuccess = () => {
    setShowPatternLock(true); // move to pattern lock screen
  };

  // Called by the PatternLockScreen when the pattern is correct
  const handlePatternSuccess = () => {
    setIsLoggedIn(true);
    setShowPatternLock(false);
  };

  // If fully logged in, show your main app or success screen
  if (isLoggedIn) {
    return (
      <div
        style={{
          textAlign: "center",
          height: "100vh",
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          backgroundColor: "#121212",
          color: "#ffffff",
          fontFamily: "'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif",
        }}
      >
        <div
          style={{
            backgroundColor: "#1e1e1e",
            padding: "30px",
            borderRadius: "12px",
            boxShadow: "0px 6px 16px rgba(0,0,0,0.3)",
            maxWidth: "400px",
            width: "80%",
            textAlign: "center",
            border: "1px solid #333333",
          }}
        >
          <h1 style={{ color: "#f0f0f0", marginBottom: "20px" }}>
            Successfully Authenticated!
          </h1>
          <p style={{ color: "#aaaaaa", fontSize: "16px" }}>
            Welcome to the secure area of the application.
          </p>
          <div
            style={{
              width: "80px",
              height: "80px",
              margin: "30px auto 20px",
              borderRadius: "50%",
              backgroundColor: "#3a6ea5",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <div
              style={{
                width: "40px",
                height: "25px",
                // Use left + bottom borders for a standard check orientation
                borderLeft: "3px solid #fff",
                borderBottom: "3px solid #fff",
                // Adjust the rotation and translation so it looks like a true "check"
                transform: "rotate(-45deg) translate(3px, 0px)",
              }}
            />
          </div>
        </div>
      </div>
    );
  }

  // If we've passed login but not yet pattern, show pattern screen
  if (showPatternLock) {
    return <PatternLockScreen onSuccess={handlePatternSuccess} />;
  }

  // Otherwise show login form
  return <LoginForm onLoginSuccess={handleLoginSuccess} />;
}

export default App;