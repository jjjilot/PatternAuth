import SwiftUI

struct LoginView: View {
    @State private var username: String = ""
    @State private var password: String = ""
    @State private var isAuthenticated: Bool = false
    @State private var showError: Bool = false
    @State private var showPatternAuth: Bool = false  // Controls full-screen modal
    @State private var loggedInUsername: String = ""  // Passes username to HomeView
    @State private var userPattern: [Int] = []  // Stores the user's pattern

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
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
            }
            .padding()
            .fullScreenCover(isPresented: $showPatternAuth) {  // Prevents drag-down dismissal
                AuthView(username: username, isAuthenticated: $isAuthenticated)
            }
            .navigationDestination(isPresented: $isAuthenticated) {
                HomeView(username: loggedInUsername)  // Pass username to HomeView
            }
        }
    }

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
                    loggedInUsername = username  // Store username for later use in HomeView
                    showError = false

                    // Check for user pattern after successful login
                    checkUserPattern()
                } else {
                    print("Login failed: \(httpResponse.statusCode)")
                    showError = true
                }
            }
        }.resume()
    }

    struct User: Decodable {
        let pattern: [Int]  // Directly decoding as an array of integers
    }

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
                            isAuthenticated = true  // Skip pattern authentication
                        } else {
                            showPatternAuth = true  // Show pattern authentication screen
                        }
                    }
                } catch {
                    print("Error decoding user pattern: \(error)")
                }
            }
        }.resume()
    }
}
