import SwiftUI
import LocalAuthentication

struct LoginView: View {
    @State private var username: String = ""
    @State private var password: String = ""
    @State private var isAuthenticated: Bool = false
    @State private var showError: Bool = false
    @State private var showPatternAuth: Bool = false
    @State private var loggedInUsername: String = ""
    @State private var userPattern: [Int] = []
    @State private var isFaceIDAuthenticated: Bool = false
    @State private var faceIDErrorMessage: String?

    // Initial app screen
    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                if isFaceIDAuthenticated {
                    Text("Login")
                        .font(.largeTitle)
                        .fontWeight(.bold)
                        .padding(.bottom, 10)

                    TextField("Username", text: $username)
                        .autocapitalization(.none)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)

                    SecureField("Password", text: $password)
                        .autocapitalization(.none)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(8)

                    if showError {
                        Text("Invalid username or password. Please try again.")
                            .foregroundColor(.red)
                            .padding(.top, 10)
                    }

                    Button(action: authenticateUser) {
                        Text("Login")
                            .frame(maxWidth: .infinity)
                            .padding()
                            .background(Color.blue)
                            .foregroundColor(.white)
                            .cornerRadius(8)
                    }
                } else {
                    Text("Authenticating with Face ID...")
                        .font(.title2)
                        .foregroundColor(.gray)
                }

                if let message = faceIDErrorMessage {
                    Text(message)
                        .foregroundColor(.red)
                        .padding()
                }
            }
            .padding()
            .onAppear(perform: authenticateWithFaceID)
            .fullScreenCover(isPresented: $showPatternAuth) {
                AuthView(username: username, isAuthenticated: $isAuthenticated)
            }
            .navigationDestination(isPresented: $isAuthenticated) {
                HomeView(username: loggedInUsername)
            }
        }
    }

    // Don't let user in until successful FaceID
    func authenticateWithFaceID() {
        let context = LAContext()
        var error: NSError?

        if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
            let reason = "Authenticate to proceed to login"

            context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, localizedReason: reason) { success, authenticationError in
                DispatchQueue.main.async {
                    if success {
                        isFaceIDAuthenticated = true
                    } else {
                        faceIDErrorMessage = "Face ID authentication failed. Please try again."
                    }
                }
            }
        } else {
            DispatchQueue.main.async {
                faceIDErrorMessage = "Face ID not available. Please enable it in settings."
            }
        }
    }
    
    // Endpoint stuff (checking user info)
    func authenticateUser() {
        guard let url = URL(string: "https://patternauth.onrender.com/login") else {
            print("Invalid URL")
            return
        }

        let body: [String: String] = ["username": username, "password": password]
        guard let jsonData = try? JSONSerialization.data(withJSONObject: body) else {
            print("Failed to encode JSON")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = jsonData

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error in request: \(error.localizedDescription)")
                DispatchQueue.main.async { showError = true }
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                print("Invalid response")
                DispatchQueue.main.async { showError = true }
                return
            }

            DispatchQueue.main.async {
                if httpResponse.statusCode == 200 {
                    print("Login successful")
                    loggedInUsername = username
                    showError = false
                    checkUserPattern()
                } else {
                    print("Login failed: \(httpResponse.statusCode)")
                    showError = true
                }
            }
        }.resume()
    }

    struct User: Decodable {
        let pattern: [Int]
    }

    // Endpoint stuff (checking pattern)
    func checkUserPattern() {
        guard let url = URL(string: "https://patternauth.onrender.com/user/\(username)") else {
            print("Invalid URL for pattern check")
            return
        }

        var request = URLRequest(url: url)
        request.httpMethod = "GET"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                print("Error fetching user pattern: \(error.localizedDescription)")
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                print("Invalid response")
                return
            }

            if httpResponse.statusCode == 200, let data = data {
                do {
                    let user = try JSONDecoder().decode(User.self, from: data)

                    DispatchQueue.main.async {
                        if user.pattern == [0, 0, 0, 0, 0, 0, 0, 0, 0] {
                            isAuthenticated = true
                        } else {
                            showPatternAuth = true
                        }
                    }
                } catch {
                    print("Error decoding user pattern: \(error)")
                }
            }
        }.resume()
    }
}
