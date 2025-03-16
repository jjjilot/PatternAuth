import React from "react";

function PatternResetScreen({ onBackToLogin }) {
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
          maxWidth: "400px",
          width: "90%",
          textAlign: "center",
          border: "1px solid #333333",
        }}
      >
        <div
          style={{
            width: "80px",
            height: "80px",
            margin: "0 auto 20px",
            borderRadius: "50%",
            backgroundColor: "#e74c3c", // Red alert color
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <div
            style={{
              fontSize: "40px",
              fontWeight: "bold",
              color: "#ffffff",
            }}
          >
            !
          </div>
        </div>

        <h2 style={{ marginBottom: "20px", color: "#f0f0f0" }}>
          Pattern Reset Required
        </h2>
        
        <p style={{ color: "#cccccc", fontSize: "14px", lineHeight: "1.6", marginBottom: "15px" }}>
          For security reasons, your pattern needs to be reset every 7 days.
        </p>
        
        <div
          style={{
            backgroundColor: "#252525",
            borderRadius: "8px",
            padding: "20px",
            margin: "20px 0",
          }}
        >
          <div
            style={{
              width: "70px",
              height: "70px",
              margin: "0 auto 15px",
              borderRadius: "15px",
              backgroundColor: "#3a6ea5",
              display: "flex",
              justifyContent: "center",
              alignItems: "center",
            }}
          >
            <div
              style={{
                width: "30px",
                height: "30px",
                borderRadius: "50%",
                border: "3px solid #ffffff",
                position: "relative",
              }}
            >
              <div
                style={{
                  position: "absolute",
                  bottom: "-10px",
                  left: "50%",
                  transform: "translateX(-50%)",
                  width: "0",
                  height: "0",
                  borderLeft: "8px solid transparent",
                  borderRight: "8px solid transparent",
                  borderTop: "10px solid #ffffff",
                }}
              />
            </div>
          </div>
          <h3 style={{ color: "#f0f0f0", marginBottom: "10px" }}>
            Pattern Auth App
          </h3>
        </div>
        
        <p style={{ color: "#aaaaaa", fontSize: "14px", lineHeight: "1.6", marginBottom: "15px" }}>
          Please follow these steps to reset your pattern:
        </p>
        
        <ol
          style={{
            textAlign: "left",
            color: "#cccccc",
            fontSize: "14px",
            lineHeight: "1.6",
            marginBottom: "20px",
            paddingLeft: "20px",
          }}
        >
          <li style={{ marginBottom: "8px" }}>Open the Pattern Auth App on your mobile device</li>
          <li style={{ marginBottom: "8px" }}>Log in with your username and password</li>
          <li style={{ marginBottom: "8px" }}>Follow the on-screen instructions to create a new pattern</li>
          <li style={{ marginBottom: "8px" }}>Return to this website and log in again</li>
        </ol>
        
        <button
          onClick={onBackToLogin}
          style={{
            width: "100%",
            padding: "12px",
            marginTop: "10px",
            borderRadius: "6px",
            border: "none",
            backgroundColor: "#3a6ea5",
            color: "white",
            cursor: "pointer",
            fontSize: "14px",
            fontWeight: "bold",
            transition: "background-color 0.2s",
          }}
          onMouseOver={(e) => (e.target.style.backgroundColor = "#457ab8")}
          onMouseOut={(e) => (e.target.style.backgroundColor = "#3a6ea5")}
        >
          Back to Login
        </button>
      </div>
    </div>
  );
}

export default PatternResetScreen;
