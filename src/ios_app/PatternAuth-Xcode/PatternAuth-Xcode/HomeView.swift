import SwiftUI

struct HomeView: View {
    @State private var selectedDots: [Int] = []
    @State private var currentPath: [CGPoint] = []
    @State private var navigateToConfirmation = false
    @State private var showAlert = false
    @State private var alertMessage = ""

    let dotSize: CGFloat = 60
    let spacing: CGFloat = 40
    var username: String  // Accept username as a parameter

    var body: some View {
        NavigationStack {
            VStack {
                Text("Enter New Pattern")
                    .font(.largeTitle)
                    .padding()

                GeometryReader { geometry in
                    let gridWidth = geometry.size.width
                    let positions = calculateGridPositions(gridWidth: gridWidth, dotSize: dotSize, spacing: spacing)

                    ZStack {
                        ForEach(0..<9, id: \.self) { index in
                            Circle()
                                .strokeBorder(Color.blue, lineWidth: 2)
                                .background(Circle().foregroundColor(selectedDots.contains(index) ? Color.blue : Color.clear))
                                .frame(width: dotSize, height: dotSize)
                                .position(positions[index])
                        }

                        if currentPath.count > 1 {
                            Path { path in
                                path.addLines(currentPath)
                            }
                            .stroke(Color.blue, lineWidth: 2)
                        }
                    }
                    .gesture(
                        DragGesture(minimumDistance: 0)
                            .onChanged { value in
                                if let index = nearestDot(to: value.location, from: positions),
                                   !selectedDots.contains(index) {
                                    selectedDots.append(index)
                                    currentPath.append(positions[index])
                                }
                            }
                    )
                }
                .frame(height: 350)
                .padding(.bottom, 20)

                Button(action: {
                    checkAndStorePattern(selectedDots)
                }) {
                    Text("Submit")
                        .padding()
                        .background(Color.blue)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                        .opacity((selectedDots.count >= 3 && selectedDots.count <= 9) ? 1.0 : 0.5)
                }
                .disabled(selectedDots.count < 3)
                .padding()

                // Reset Button
                Button(action: {
                    resetGrid()
                }) {
                    Text("Reset")
                        .padding()
                        .background(Color.red)
                        .foregroundColor(.white)
                        .cornerRadius(8)
                }
                .padding()
                
                .navigationDestination(isPresented: $navigateToConfirmation) {
                    ConfirmationView(pattern: selectedDots)
                }
            }
        }
        .alert(isPresented: $showAlert) {
            Alert(title: Text("Pattern Error"), message: Text(alertMessage), dismissButton: .default(Text("OK")))
        }
    }

    private func resetGrid() {
        selectedDots.removeAll()
        currentPath.removeAll()
    }
    
    private func calculateGridPositions(gridWidth: CGFloat, dotSize: CGFloat, spacing: CGFloat) -> [CGPoint] {
        let startX = (gridWidth - (2 * spacing + 3 * dotSize)) / 2 + dotSize / 2
        let startY: CGFloat = 100
        var positions: [CGPoint] = []

        for row in 0..<3 {
            for col in 0..<3 {
                let x = startX + CGFloat(col) * (dotSize + spacing)
                let y = startY + CGFloat(row) * (dotSize + spacing)
                positions.append(CGPoint(x: x, y: y))
            }
        }
        return positions
    }

    private func nearestDot(to point: CGPoint, from positions: [CGPoint]) -> Int? {
        for (index, position) in positions.enumerated() {
            if hypot(position.x - point.x, position.y - point.y) < dotSize / 2 {
                return index
            }
        }
        return nil
    }

    private func checkAndStorePattern(_ newPattern: [Int]) {
        guard let url = URL(string: "https://patternauth.onrender.com/verify-pattern") else {
            print("Invalid URL")
            return
        }

        let body: [String: Any] = [
            "username": username,
            "pattern": newPattern
        ]

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
                print("Error verifying pattern: \(error.localizedDescription)")
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                print("Invalid response")
                return
            }

            DispatchQueue.main.async {
                if httpResponse.statusCode == 200 {
                    // The pattern matches the stored one, so prompt the user to enter a different one.
                    alertMessage = "New pattern must be different from the current pattern."
                    showAlert = true
                } else if httpResponse.statusCode == 401 {
                    // The pattern is different, so update it
                    storePattern(newPattern)
                } else {
                    print("Unexpected response: \(httpResponse.statusCode)")
                }
            }
        }.resume()
    }

    private func storePattern(_ pattern: [Int]) {
        guard let url = URL(string: "https://patternauth.onrender.com/update-pattern/") else {
            print("Invalid URL")
            return
        }

        let body: [String: Any] = [
            "username": username,
            "pattern": pattern
        ]

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
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                print("Invalid response")
                return
            }

            DispatchQueue.main.async {
                if httpResponse.statusCode == 200 {
                    print("Pattern updated successfully")
                    navigateToConfirmation = true
                } else {
                    print("Failed to update pattern - Status Code: \(httpResponse.statusCode)")
                }
            }
        }.resume()
    }
}

struct HomeView_Previews: PreviewProvider {
    static var previews: some View {
        HomeView(username: "testuser")
    }
}
