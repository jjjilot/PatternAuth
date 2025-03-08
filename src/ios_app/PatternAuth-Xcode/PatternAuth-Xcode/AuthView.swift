import SwiftUI

struct AuthView: View {
    let username: String
    @Binding var isAuthenticated: Bool
    @State private var selectedDots: [Int] = []
    @State private var currentPath: [CGPoint] = []
    @State private var showError: Bool = false
    @Environment(\.dismiss) var dismiss // Allows closing the modal

    let dotSize: CGFloat = 60
    let spacing: CGFloat = 40

    var body: some View {
        VStack {
            Text("Enter Your Pattern")
                .font(.title)
                .fontWeight(.bold)
                .padding()

            GeometryReader { geometry in
                let gridWidth = geometry.size.width
                let positions = calculateGridPositions(gridWidth: gridWidth, dotSize: dotSize, spacing: spacing)

                ZStack {
                    // Draw circles
                    ForEach(0..<9, id: \.self) { index in
                        Circle()
                            .strokeBorder(Color.blue, lineWidth: 2)
                            .background(Circle().foregroundColor(selectedDots.contains(index) ? Color.blue : Color.clear))
                            .frame(width: dotSize, height: dotSize)
                            .position(positions[index])
                    }

                    // Draw pattern path
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
                        .onEnded { _ in
                            if !selectedDots.isEmpty {
                                verifyPattern()
                            }
                        }
                )
            }
            .frame(height: 350)
            .padding(.bottom, 20)

            if showError {
                Text("Incorrect pattern. Try again.")
                    .foregroundColor(.red)
                    .padding()
            }

            Button("Reset") {
                selectedDots.removeAll()
                currentPath.removeAll()
                showError = false
            }
            .padding()
            .background(Color.gray)
            .foregroundColor(.white)
            .cornerRadius(8)
        }
        .padding()
    }

    private func verifyPattern() {
        guard let url = URL(string: "https://patternauth.onrender.com/verify-pattern") else {
            print("Invalid URL")
            return
        }

        let body: [String: Any] = ["username": username, "pattern": selectedDots]
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
                    print("Pattern correct, navigating to HomeView")
                    isAuthenticated = true
                    dismiss() // Closes modal and triggers HomeView navigation
                } else {
                    print("Incorrect pattern")
                    showError = true
                    selectedDots.removeAll()
                    currentPath.removeAll()
                }
            }
        }.resume()
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
        let detectionRadius: CGFloat = dotSize * 0.75 // Increased detection radius for better swipe registration
        return positions.enumerated()
            .filter { hypot($0.element.x - point.x, $0.element.y - point.y) < detectionRadius }
            .map { $0.offset }
            .first
    }
}

struct AuthView_Previews: PreviewProvider {
    static var previews: some View {
        AuthView(username: "testuser", isAuthenticated: .constant(false))
    }
}
